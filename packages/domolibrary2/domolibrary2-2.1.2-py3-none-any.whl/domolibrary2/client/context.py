from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass(slots=True)
class RouteContext:
    """Context for route and client calls.

    This bundles transport and logging-related options so that class methods
    can construct a single object and pass it down into route functions and
    the HTTP client layer.
    """

    session: httpx.AsyncClient | None = None
    debug_api: bool = False
    debug_num_stacks_to_drop: int = 1
    parent_class: Optional[str] = None
    log_level: Optional[str] = None
