"""
Jupyter Content Management Functions

This module provides functions for managing content within Jupyter workspaces.
"""

__all__ = [
    "get_jupyter_content",
    "create_jupyter_obj",
    "delete_jupyter_content",
    "update_jupyter_file",
    "get_content",
    "get_content_recursive",
    # Utility functions
    "generate_update_jupyter_body__new_content_path",
    "generate_update_jupyter_body__text",
    "generate_update_jupyter_body__ipynb",
    "generate_update_jupyter_body__directory",
    "GenerateUpdateJupyterBodyFactory",
    "generate_update_jupyter_body",
]

import asyncio
import os
import urllib
from enum import Enum, member
from functools import partial
from typing import Any, Optional

import httpx

from ... import auth as dmda
from ...base.base import DomoEnumMixin
from ...client import (
    get_data as gd,
    response as rgd,
)
from ...utils import chunk_execution as dmce
from .exceptions import (
    Jupyter_CRUD_Error,
    Jupyter_GET_Error,
    SearchJupyterNotFoundError,
)


# Utility functions for body generation
def generate_update_jupyter_body__new_content_path(content_path):
    """Generate new content path for jupyter body."""
    if not content_path:
        return ""

    ## replaces ./ if passed as part of url description
    if content_path.startswith("./"):
        content_path = content_path[2:]

    if "/" in content_path:
        return "/".join(content_path.split("/")[:-1])
    else:
        return ""


def generate_update_jupyter_body__text(body, content_path=None):
    """Generate body for text content type."""
    body.update(
        {
            "format": "text",
            "path": generate_update_jupyter_body__new_content_path(content_path),
            "type": "file",
        }
    )
    return body


def generate_update_jupyter_body__ipynb(body, content_path=None):
    """Generate body for ipynb (Jupyter notebook) content type."""
    body.update(
        {
            "format": "json",
            "path": generate_update_jupyter_body__new_content_path(content_path),
            "type": "notebook",
        }
    )
    return body


def generate_update_jupyter_body__directory(content_path, body):
    """Generate body for directory content type."""
    body.update(
        {
            "path": generate_update_jupyter_body__new_content_path(content_path),
            "format": None,
            "type": "directory",
        }
    )
    return body


class GenerateUpdateJupyterBodyFactory(DomoEnumMixin, Enum):
    """Factory for generating different types of Jupyter request bodies."""

    IPYNB = member(partial(generate_update_jupyter_body__ipynb))
    DIRECTORY = member(partial(generate_update_jupyter_body__directory))
    TEXT = member(partial(generate_update_jupyter_body__text))
    default = member(partial(generate_update_jupyter_body__text))


def generate_update_jupyter_body(
    new_content: Any,
    content_path: str,  # my_folder/datatypes.ipynb
):
    """Factory to construct properly formed body for Jupyter API requests.

    Args:
        new_content: Content to be included in the body
        content_path: Path of the content (determines content type)

    Returns:
        Dictionary containing properly formatted body for Jupyter API
    """

    if content_path.startswith("./"):
        content_path = content_path[2:]

    content_name = os.path.normpath(content_path).split(os.sep)[-1]

    if "." in content_path:
        content_type = content_path.split(".")[-1]
    else:
        content_type = "directory"

    body = {
        "name": content_name,
        "content": new_content,
        "path": content_path,
    }
    return GenerateUpdateJupyterBodyFactory.get(content_type).value(
        body=body, content_path=content_path
    )


@gd.route_function
async def get_jupyter_content(
    auth: dmda.DomoJupyterAuth,
    content_path: str = "",
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    is_run_test_jupyter_auth: bool = True,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Retrieve content from a Jupyter workspace.

        Args:
            auth: Jupyter authentication object with workspace credentials
            content_path: Path to content within the workspace (default: root)
            session: Optional httpx client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output
            parent_class: Optional parent class name for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object containing workspace content

        Raises:
            Jupyter_GET_Error: If content retrieval fails
            SearchJupyterNotFoundError
    : If content path doesn't exist
    """
    if is_run_test_jupyter_auth:
        dmda.test_is_jupyter_auth(auth)

    url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/{content_path}"

    res = await gd.get_data(
        url=f"{url}",
        method="GET",
        auth=auth,
        headers={"authorization": f"Token {auth.jupyter_token}"},
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 403:
        raise Jupyter_GET_Error(
            message="Unable to query API, valid jupyter_token?", res=res
        )

    if res.status == 404:
        raise SearchJupyterNotFoundError(
            search_criteria=f"content_path: {content_path}", res=res
        )

    if not res.is_success:
        raise Jupyter_GET_Error(message="Failed to retrieve Jupyter content", res=res)

    return res


@gd.route_function
async def create_jupyter_obj(
    auth: dmda.DomoJupyterAuth,
    new_content: Any = "",
    content_path: str = "",
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Create new content in a Jupyter workspace.

    Args:
        auth: Jupyter authentication object with workspace credentials
        new_content: Content to create (text, notebook data, etc.)
        content_path: File name and location within the workspace
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing creation result

    Raises:
        Jupyter_CRUD_Error: If content creation fails
    """
    dmda.test_is_jupyter_auth(auth)

    # removes ./ jic
    if content_path.startswith("./"):
        content_path = content_path[2:]

    body = generate_update_jupyter_body(
        new_content=new_content, content_path=content_path
    )

    content_path_split = os.path.normpath(content_path).split(os.sep)

    # new content gets created as "untitled folder" // removes the 'future name' and saves for later
    content_path_split.pop(-1)

    base_url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/"

    res_post = await gd.get_data(
        url=f"{base_url}{'/'.join(content_path_split)}",
        method="POST",
        auth=auth,
        body=body,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res_post

    if res_post.status == 403:
        raise Jupyter_CRUD_Error(
            operation="create",
            content_path=content_path,
            message="Unable to query API, valid jupyter_token?",
            res=res_post,
        )

    if not res_post.is_success:
        raise Jupyter_CRUD_Error(
            operation="create", content_path=content_path, res=res_post
        )

    # untitled_folder
    url = urllib.parse.urljoin(base_url, res_post.response["path"])

    # created a folder "untitled folder"
    await asyncio.sleep(3)

    res = await gd.get_data(
        url=urllib.parse.quote(url, safe="/:?=&"),
        method="PATCH",
        auth=auth,
        body={"path": content_path, "content": new_content},
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if res.status == 403:
        raise Jupyter_CRUD_Error(
            operation="rename",
            content_path=content_path,
            message="Unable to query API, valid jupyter_token?",
            res=res,
        )

    if res.status == 409:
        raise Jupyter_CRUD_Error(
            operation="rename",
            content_path=content_path,
            message="Conflict during PATCH - does the content already exist?",
            res=res,
        )

    if not res.is_success:
        raise Jupyter_CRUD_Error(operation="rename", content_path=content_path, res=res)

    res.response = {**res_post.response, **res.response}

    return res


@gd.route_function
async def delete_jupyter_content(
    auth: dmda.DomoJupyterAuth,
    content_path: str,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Delete content from a Jupyter workspace.

        Args:
            auth: Jupyter authentication object with workspace credentials
            content_path: File name and location within the workspace
            session: Optional httpx client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output
            parent_class: Optional parent class name for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object containing deletion result

        Raises:
            Jupyter_CRUD_Error: If content deletion fails
            SearchJupyterNotFoundError
    : If content path doesn't exist
    """
    dmda.test_is_jupyter_auth(auth)

    base_url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/"

    url = urllib.parse.urljoin(base_url, content_path)
    url = urllib.parse.quote(url, safe="/:?=&")

    res = await gd.get_data(
        url=url,
        method="DELETE",
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 403:
        raise Jupyter_CRUD_Error(
            operation="delete",
            content_path=content_path,
            message="Unable to query API, valid jupyter_token?",
            res=res,
        )

    if res.status == 404:
        raise SearchJupyterNotFoundError(
            search_criteria=f"content_path: {content_path}", res=res
        )

    if not res.is_success:
        raise Jupyter_CRUD_Error(operation="delete", content_path=content_path, res=res)

    return res


@gd.route_function
async def update_jupyter_file(
    auth: dmda.DomoJupyterAuth,
    new_content: Any,
    content_path: str = "",
    body: Optional[dict] = None,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Update content in a Jupyter workspace file.

        Args:
            auth: Jupyter authentication object with workspace credentials
            new_content: New content to update the file with
            content_path: File name and location within the workspace
            body: Optional custom body for the request
            session: Optional httpx client session for connection reuse
            debug_api: Enable detailed API request/response logging
            debug_num_stacks_to_drop: Number of stack frames to drop in debug output
            parent_class: Optional parent class name for debugging context
            return_raw: Return raw API response without processing

        Returns:
            ResponseGetData object containing update result

        Raises:
            Jupyter_CRUD_Error: If file update fails
            SearchJupyterNotFoundError
    : If content path doesn't exist
    """
    dmda.test_is_jupyter_auth(auth)

    body = body or generate_update_jupyter_body(new_content, content_path)

    os.path.normpath(content_path).split(os.sep)

    base_url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/"

    url = urllib.parse.urljoin(base_url, content_path)
    url = urllib.parse.quote(url, safe="/:?=&")

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        body=body,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if return_raw:
        return res

    if res.status == 403:
        raise Jupyter_CRUD_Error(
            operation="update",
            content_path=content_path,
            message="Unable to query API, valid jupyter_token?",
            res=res,
        )

    if res.status == 404:
        raise SearchJupyterNotFoundError(
            search_criteria=f"content_path: {content_path}", res=res
        )

    if not res.is_success:
        raise Jupyter_CRUD_Error(operation="update", content_path=content_path, res=res)

    return res


async def get_content_recursive(
    auth: dmda.DomoJupyterAuth,
    all_rows: list,
    content_path: str,
    res: rgd.ResponseGetData,
    seen_paths: set,
    obj: dict = None,
    ignore_folders: list[str] = None,
    included_filetypes: list[str] = None,
    is_recursive: bool = True,
    is_run_test_jupyter_auth: bool = True,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 0,
    parent_class: Optional[str] = None,
    session: httpx.AsyncClient = None,
):
    """Recursively retrieve content from a Jupyter workspace.

    Args:
        auth: Jupyter authentication object
        all_rows: Accumulator list for all content items
        content_path: Current path being processed
        res: Response object to update
        seen_paths: Set of paths already processed (for deduplication)
        obj: Current content object (None on initial call)
        ignore_folders: Folder names to exclude (matches path segments)
        included_filetypes: File extensions to include (e.g., ['.ipynb', '.py'])
        is_recursive: Whether to recursively traverse directories
        is_run_test_jupyter_auth: Test auth on first call
        return_raw: Return raw response
        debug_api: Enable API debugging
        debug_num_stacks_to_drop: Stack frames to drop in debug output
        parent_class: Parent class name for debugging
        session: Optional httpx client session

    Returns:
        ResponseGetData with all content in response attribute (deduplicated)
    """
    ignore_folders = ignore_folders or []
    included_filetypes = included_filetypes or []

    # Fetch content object on initial call
    if not obj:
        obj_res = await get_jupyter_content(
            auth=auth,
            content_path=content_path,
            return_raw=return_raw,
            debug_api=debug_api,
            debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
            parent_class=parent_class,
            is_run_test_jupyter_auth=is_run_test_jupyter_auth,
            session=session,
        )
        obj = obj_res.response
        if not res:
            res = obj_res

    # Deduplication: skip if we've already processed this path
    obj_path = obj.get("path", "")
    if obj_path in seen_paths:
        return res

    # Mark path as seen and add to results
    seen_paths.add(obj_path)
    all_rows.append(obj)

    # Early return if not a directory
    if obj.get("type") != "directory":
        res.response = all_rows
        return res

    # Early return if not recursive
    if not is_recursive:
        res.response = all_rows
        return res

    # Get directory contents
    obj_content = obj.get("content", [])

    # Single-pass filtering: combine all filter logic
    filtered_content = []
    for item in obj_content:
        if not isinstance(item, dict):
            continue

        item_name = item.get("name", "")
        item_path = item.get("path", "")
        item_type = item.get("type", "")

        # Skip if already seen
        if item_path in seen_paths:
            continue

        # Skip .ipynb_checkpoints
        if item_name == ".ipynb_checkpoints":
            continue

        # Skip ignored folders (check path segments)
        if ignore_folders and any(
            ign in item_path.split("/") for ign in ignore_folders
        ):
            continue

        # Skip recent_executions folder
        if "recent_executions" in item_path:
            continue

        # For directories, always include (needed for recursion)
        if item_type == "directory":
            filtered_content.append(item)
            continue

        # For files, apply filetype filter if specified
        if included_filetypes:
            if any(item_name.endswith(ext) for ext in included_filetypes):
                filtered_content.append(item)
        else:
            # No filter specified, include all files
            filtered_content.append(item)

    # Update response
    res.response = all_rows

    # Recursively process subdirectories
    if filtered_content:
        await dmce.gather_with_concurrency(
            *[
                get_content_recursive(
                    auth=auth,
                    content_path=item["path"],
                    all_rows=all_rows,
                    res=res,
                    seen_paths=seen_paths,
                    ignore_folders=ignore_folders,
                    included_filetypes=included_filetypes,
                    is_recursive=is_recursive,
                    is_run_test_jupyter_auth=False,
                    debug_api=debug_api,
                    debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
                    parent_class=parent_class,
                    session=session,
                )
                for item in filtered_content
            ],
            n=5,
        )

    return res


@gd.route_function
async def get_content(
    auth: dmda.DomoJupyterAuth,
    content_path: str = "",
    ignore_folders: list[str] = None,
    included_filetypes: list[str] = None,
    is_recursive: bool = True,
    session: httpx.AsyncClient | None = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 2,
    parent_class: Optional[str] = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    """Get content from a Jupyter workspace recursively.

    Args:
        auth: Jupyter authentication object with workspace credentials
        content_path: Path to start retrieving content from
        ignore_folders: Folder names to exclude (matches path segments)
        included_filetypes: File extensions to include (e.g., ['.ipynb', '.py', '.md'])
        is_recursive: Whether to recursively get nested directory content
        session: Optional httpx client session for connection reuse
        debug_api: Enable detailed API request/response logging
        debug_num_stacks_to_drop: Number of stack frames to drop in debug output
        parent_class: Optional parent class name for debugging context
        return_raw: Return raw API response without processing

    Returns:
        ResponseGetData object containing all workspace content (deduplicated)

    Raises:
        Jupyter_GET_Error: If content retrieval fails
        SearchJupyterNotFoundError: If content path doesn't exist
    """
    dmda.test_is_jupyter_auth(auth)

    all_rows = []
    seen_paths = set()
    res = None

    return await get_content_recursive(
        auth=auth,
        content_path=content_path,
        all_rows=all_rows,
        res=res,
        seen_paths=seen_paths,
        ignore_folders=ignore_folders,
        included_filetypes=included_filetypes,
        is_recursive=is_recursive,
        is_run_test_jupyter_auth=False,
        return_raw=return_raw,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )
