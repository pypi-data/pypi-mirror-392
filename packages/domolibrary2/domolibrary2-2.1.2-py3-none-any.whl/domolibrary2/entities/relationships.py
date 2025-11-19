"""
Unified relationship system for Domo entities.

Provides a comprehensive relationship modeling system that unifies
all types of entity interactions including access control, membership,
sharing, and other relationship types within the Domo ecosystem.

Classes:
    DomoRelationship: Represents a relationship between two entities
    DomoRelationshipController: Manages relationships for entities
"""

from .base import DomoBase, DomoEnum
from .entities import DomoEntity
from abc import abstractmethod
from ..utils import chunk_execution as dmce
from dataclasses import dataclass, field
from typing import Any, Dict, List

RelationshipType = DomoEnum
"""Types of relationships between Domo entities."""

# Access and Permission Relationships
# OWNER = "owner"
# ADMIN = "admin"
# EDITOR = "editor"
# PARTICIPANT = "participant"
# VIEWER = "viewer"

# # Membership Relationships
# MEMBER = "member"
# OWNER = "owner"

# # LIneage
# PARENT = "parent"
# CHILD = "child"


@dataclass
class DomoRelationship(DomoBase):
    """Represents a relationship between two Domo entities.

    This unified relationship model can represent any type of connection
    between Domo entities including access control, membership, sharing,
    subscriptions, and organizational structures.

    Attributes:
    """

    relative_id: str
    relative_class: DomoEntity = field(repr=False)
    relationship_type: RelationshipType

    # Core relationship identifiers
    parent_entity: DomoEntity = field(repr=False, default=None)
    relative_entity: DomoEntity = field(repr=False, default=None)

    def __eq__(self, other):
        return (
            self.parent_id == other.parent_id
            and self.relationship_type == other.relationship_type
            and self.relative_id == other.relative_id
        )

    async def get_relative(self):
        assert hasattr(
            self.relative_class, "get_entity_by_id"
        ), "relative_class must implement get_entity_by_id method"
        return await self.relative_class.get_entity_by_id(
            entity_id=self.relative_id, auth=self.parent_entity.auth
        )

    @property
    def parent_id(self):
        return self.parent_entity.id

    metadata: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def to_dict(self) -> str:
        """Convert relationship to JSON string."""
        raise NotImplementedError("Subclasses must implement to_dict method.")

    @abstractmethod
    def update(self):
        """Update relationship metadata or properties."""
        raise NotImplementedError("Subclasses must implement update method.")


@dataclass
class DomoRelationshipController(DomoBase):
    """Controller for managing Domo entity relationships.

    This class provides high-level operations for creating, managing, and
    querying relationships between Domo entities. It serves as the primary
    interface for relationship operations.

    will be implemented as DomoDataset.Relations
    with methods Relations.get_owners(), get_members(), add_owners(), add_members()
    """

    relationships: List[DomoRelationship] = field(default_factory=list)

    async def get_relative_entities(self):
        """retrieves relative entities for each relationship
        not the same as getting the parent objects' relationships
        """
        await dmce.gather_with_concurrency(
            *[relationship.get_relative() for relationship in self.relationships], n=10
        )

        return self.relationships

    @abstractmethod
    def add_relationship(
        self,
        relative_id,
        relationship_type: RelationshipType,
    ) -> DomoRelationship:
        """Create a new relationship between entities."""

    @abstractmethod
    def get(
        self,
    ) -> List[DomoRelationship]:
        """Find relationships matching the specified criteria."""
        raise NotImplementedError("Subclasses must implement get method.")


__all__ = [
    "RelationshipType",
    "DomoRelationship",
    "DomoRelationshipController",
]
