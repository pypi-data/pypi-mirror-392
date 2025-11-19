"""Base entity classes for Domo objects with inheritance hierarchy and lineage support.

This module provides the foundational classes for all Domo entities including datasets,
cards, pages, users, and groups. It implements a hierarchical structure with support
for entity relationships, lineage tracking, and federation.

Classes:
    DomoEntity: Base entity with core functionality
    DomoEntity_w_Lineage: Entity with lineage tracking capabilities
    DomoManager: Base class for entity managers
    DomoSubEntity: Entity that belongs to a parent entity
"""

from ..client.auth import DomoAuth
from .base import DomoBase
import abc
from dataclasses import dataclass, field, fields

from typing import Any, Callable, Optional

from ..utils.convert import convert_snake_to_pascal
from ..client import auth as dmda


@dataclass
class DomoEntity(DomoBase):
    """Base class for all Domo entities (datasets, cards, pages, users, etc.).

    Provides core functionality including authentication, unique identification,
    data conversion utilities, and relationship management. All concrete entity
    types should inherit from this class or one of its subclasses.

    Attributes:
        auth: Authentication object for API requests (hidden in repr)
        id: Unique identifier for the entity
        raw: Raw API response data for the entity (hidden in repr)
        Relations: Relationship controller for managing entity relationships

    Example:
        >>> entity = SomeDomoEntity(auth=auth, id="123", raw={})
        >>> entity.display_url()  # Implemented by subclass
        'https://mycompany.domo.com/...'
    """

    auth: dmda.DomoAuth = field(repr=False)
    id: str
    raw: dict = field(repr=False)  # api representation of the class

    Relations: Any = field(repr=False, default=None)

    # logger: Logger = field(repr=False) ## pass global logger

    def __post_init__(self):
        """Initialize entity with relationship controller."""
        from .relationships import DomoRelationshipController

        self.Relations = DomoRelationshipController(auth=self.auth, parent_entity=self)

    @property
    def _name(self) -> str:
        name = getattr(self, "name", None)

        if not name:
            raise NotImplementedError(
                "This property should be implemented by subclasses."
            )
        return name

    def __eq__(self, other) -> bool:
        """Check equality based on entity ID and class type.

        Args:
            other: Object to compare with

        Returns:
            bool: True if both are the same class type with the same ID
        """
        if self.__class__.__name__ != other.__class__.__name__:
            return False

        return self.id == other.id

    def to_dict(self, override_fn: Optional[Callable] = None) -> dict:
        """Convert all dataclass attributes to a dictionary in pascalCase.

        This method is useful for serializing entity data for API requests
        or data export operations.

        Args:
            override_fn (Optional[Callable]): Custom conversion function to override default behavior

        Returns:
            dict: Dictionary with pascalCase keys and corresponding attribute values

        Example:
            >>> entity.to_dict()
            {'entityId': '123', 'displayName': 'My Entity', ...}
        """

        if override_fn:
            return override_fn(self)

        return {
            convert_snake_to_pascal(field.name): getattr(self, field.name)
            for field in fields(self)
        }

    @property
    @abc.abstractmethod
    def entity_type(self) -> str:
        """Get the EntityType for this entity based on its class name."""
        return self.__class__.__name__

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, auth: DomoAuth, obj: dict):
        """Create an entity instance from a dictionary representation.

        This method should be implemented by subclasses to handle the conversion
        from API response dictionaries to entity objects.

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @classmethod
    @abc.abstractmethod
    async def get_by_id(cls, auth: DomoAuth, id: str):
        """Fetch an entity by its unique identifier.

        This method should be implemented by subclasses to handle entity-specific
        retrieval logic from the Domo API.

        Args:
            auth (DomoAuth): Authentication object for API requests
            entity_id (str): Unique identifier of the entity to retrieve

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @classmethod
    @abc.abstractmethod
    async def get_entity_by_id(cls, auth: dmda.DomoAuth, entity_id: str):
        """Fetch an entity by its ID

        This method should be implemented by subclasses to fetch the specific
        entity type while ensuring lineage tracking is properly initialized.

        Args:
            auth (DomoAuth): Authentication object for API requests
            entity_id (str): Unique identifier of the entity to retrieve

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    def display_url(self) -> str:
        """Generate the URL to display this entity in the Domo interface.

        This method should return the direct URL to view the entity in Domo's
        web interface, allowing users to navigate directly to the entity.

        Returns:
            str: Complete URL to view the entity in Domo

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


@dataclass
class DomoEntity_w_Lineage(DomoEntity):
    """Entity with lineage tracking capabilities.

    Extends DomoEntity to include lineage tracking functionality,
    enabling entities to track their relationships and dependencies
    within the Domo ecosystem.

    Attributes:
        Lineage: Lineage tracking object for dependency management (hidden in repr)
    """

    Lineage: Any = field(repr=False)

    def __post_init__(self):
        """Initialize lineage tracking after entity creation."""
        from ..classes.subentity import DomoLineage as dmdl

        # Using protected method until public interface is available
        self.Lineage = dmdl.DomoLineage.from_parent(auth=self.auth, parent=self)

        super().__post_init__()


@dataclass
class DomoManager(DomoBase):
    """Base class for entity managers that handle collections of entities.

    Provides the foundation for manager classes that handle operations
    on collections of entities (e.g., DatasetManager, CardManager).

    Attributes:
        auth: Authentication object for API requests (hidden in repr)
    """

    auth: dmda.DomoAuth = field(repr=False)

    @abc.abstractmethod
    async def get(self, *args, **kwargs):
        """Retrieve entities based on provided criteria.

        Must be implemented by subclasses to handle entity-specific
        retrieval and filtering logic.

        Args:
            *args: Positional arguments for entity retrieval
            **kwargs: Keyword arguments for filtering and options

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


@dataclass
class DomoSubEntity(DomoEntity):
    """Base class for entities that belong to a parent entity.

    Handles entities that are sub-components of other entities,
    such as columns in a dataset or slides in a page. Automatically
    inherits authentication and parent references.

    Attributes:
        parent: Reference to the parent entity
        auth: Authentication object (inherited from parent, hidden in repr)
    """

    parent: DomoEntity
    auth: dmda.DomoAuth = field(repr=False)

    @property
    def parent_id(self):
        return self.parent.id

    @property
    def auth(self):
        return self.parent.auth

    @classmethod
    def from_parent(cls, parent: DomoEntity):
        """Create a sub-entity instance from a parent entity.

        Args:
            parent (DomoEntity): The parent entity to derive from

        Returns:
            DomoSubEntity: New sub-entity instance with inherited properties
        """
        return cls(parent=parent)
