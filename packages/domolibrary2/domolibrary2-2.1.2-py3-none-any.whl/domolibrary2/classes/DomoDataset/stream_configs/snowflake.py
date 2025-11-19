"""Snowflake stream configuration mappings."""

from dataclasses import dataclass

from ..stream_config import StreamConfig_Mapping, register_mapping

__all__ = [
    "SnowflakeMapping",
    "SnowflakeFederatedMapping",
    "SnowflakeInternalUnloadMapping",
    "SnowflakeKeypairAuthMapping",
    "SnowflakeKeypairInternalManagedUnloadMapping",
    "SnowflakeUnloadV2Mapping",
    "SnowflakeWritebackMapping",
]


@register_mapping("snowflake")
@dataclass
class SnowflakeMapping(StreamConfig_Mapping):
    """Snowflake data provider mapping."""

    data_provider_type: str = "snowflake"
    sql: str = "query"
    warehouse: str = "warehouseName"
    database_name: str = "databaseName"


@register_mapping("snowflake_federated")
@dataclass
class SnowflakeFederatedMapping(StreamConfig_Mapping):
    """Snowflake federated data provider mapping."""

    data_provider_type: str = "snowflake_federated"


@register_mapping("snowflake-internal-unload")
@dataclass
class SnowflakeInternalUnloadMapping(StreamConfig_Mapping):
    """Snowflake internal unload data provider mapping."""

    data_provider_type: str = "snowflake-internal-unload"
    sql: str = "customQuery"
    database_name: str = "databaseName"
    warehouse: str = "warehouseName"


@register_mapping("snowflakekeypairauthentication")
@dataclass
class SnowflakeKeypairAuthMapping(StreamConfig_Mapping):
    """Snowflake keypair authentication data provider mapping."""

    data_provider_type: str = "snowflakekeypairauthentication"
    sql: str = "query"
    database_name: str = "databaseName"
    warehouse: str = "warehouseName"


@register_mapping("snowflake-keypair-internal-managed-unload")
@dataclass
class SnowflakeKeypairInternalManagedUnloadMapping(StreamConfig_Mapping):
    """Snowflake keypair internal managed unload data provider mapping."""

    data_provider_type: str = "snowflake-keypair-internal-managed-unload"
    sql: str = "customQuery"
    database_name: str = "databaseName"
    warehouse: str = "warehouseName"


@register_mapping("snowflake_unload_v2")
@dataclass
class SnowflakeUnloadV2Mapping(StreamConfig_Mapping):
    """Snowflake unload v2 data provider mapping."""

    data_provider_type: str = "snowflake_unload_v2"
    sql: str = "query"
    warehouse: str = "warehouseName"
    database_name: str = "databaseName"


@register_mapping("snowflake-writeback")
@dataclass
class SnowflakeWritebackMapping(StreamConfig_Mapping):
    """Snowflake writeback data provider mapping."""

    data_provider_type: str = "snowflake-writeback"
    table_name: str = "enterTableName"
    database_name: str = "databaseName"
    warehouse: str = "warehouseName"
