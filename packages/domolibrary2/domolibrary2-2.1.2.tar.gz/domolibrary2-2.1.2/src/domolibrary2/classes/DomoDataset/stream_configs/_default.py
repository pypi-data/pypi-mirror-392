"""Default stream configuration mapping for unknown provider types."""

from dataclasses import dataclass

from ..stream_config import StreamConfig_Mapping, register_mapping

__all__ = [
    "DefaultMapping",
]


@register_mapping("default")
@dataclass
class DefaultMapping(StreamConfig_Mapping):
    """Default data provider mapping for unknown types."""

    data_provider_type: str = "default"
    is_default: bool = True
