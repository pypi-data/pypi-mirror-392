"""AWS stream configuration mappings."""

from dataclasses import dataclass

from ..stream_config import StreamConfig_Mapping, register_mapping

__all__ = [
    "AWSAthenaMapping",
    "AmazonAthenaHighBandwidthMapping",
    "AmazonS3AssumeRoleMapping",
]


@register_mapping("aws-athena")
@dataclass
class AWSAthenaMapping(StreamConfig_Mapping):
    """AWS Athena data provider mapping."""

    data_provider_type: str = "aws-athena"
    sql: str = "query"
    database_name: str = "databaseName"
    table_name: str = "tableName"


@register_mapping("amazon-athena-high-bandwidth")
@dataclass
class AmazonAthenaHighBandwidthMapping(StreamConfig_Mapping):
    """Amazon Athena high bandwidth data provider mapping."""

    data_provider_type: str = "amazon-athena-high-bandwidth"
    sql: str = "enteredCustomQuery"
    database_name: str = "databaseName"


@register_mapping("amazon_s3_assumerole")
@dataclass
class AmazonS3AssumeRoleMapping(StreamConfig_Mapping):
    """Amazon S3 assume role data provider mapping."""

    data_provider_type: str = "amazon_s3_assumerole"
    s3_bucket_category: str = "filesDiscovery"
