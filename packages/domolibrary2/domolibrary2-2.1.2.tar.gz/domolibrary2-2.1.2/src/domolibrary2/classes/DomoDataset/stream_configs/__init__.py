"""Stream configuration mappings organized by platform.

This package contains stream configuration mapping subclasses organized by
major platform (Snowflake, AWS, Domo, Google, etc.). Each mapping is
automatically registered using the @register_mapping decorator.

To add a new mapping:
1. Choose the appropriate platform file (or create a new one)
2. Define a subclass of StreamConfig_Mapping
3. Decorate it with @register_mapping("provider-name")
4. Import it in this __init__.py file

Example:
    from ..stream_config import StreamConfig_Mapping, register_mapping

    @register_mapping("my-provider")
    @dataclass
    class MyProviderMapping(StreamConfig_Mapping):
        data_provider_type: str = "my-provider"
        sql: str = "query"
"""

# Import all platform-specific mappings to trigger registration
from . import _default, aws, domo, google, other, snowflake

__all__ = [
    "_default",
    "aws",
    "domo",
    "google",
    "snowflake",
    "other",
]
