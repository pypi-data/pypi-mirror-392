"""Other/miscellaneous stream configuration mappings."""

from dataclasses import dataclass

from ..stream_config import StreamConfig_Mapping, register_mapping

__all__ = [
    "AdobeAnalyticsV2Mapping",
    "PostgreSQLMapping",
    "QualtricsMapping",
    "SharePointOnlineMapping",
]


@register_mapping("adobe-analytics-v2")
@dataclass
class AdobeAnalyticsV2Mapping(StreamConfig_Mapping):
    """Adobe Analytics v2 data provider mapping."""

    data_provider_type: str = "adobe-analytics-v2"
    sql: str = "query"
    adobe_report_suite_id: str = "report_suite_id"


@register_mapping("postgresql")
@dataclass
class PostgreSQLMapping(StreamConfig_Mapping):
    """PostgreSQL data provider mapping."""

    data_provider_type: str = "postgresql"
    sql: str = "query"


@register_mapping("qualtrics")
@dataclass
class QualtricsMapping(StreamConfig_Mapping):
    """Qualtrics data provider mapping."""

    data_provider_type: str = "qualtrics"
    qualtrics_survey_id: str = "survey_id"


@register_mapping("sharepointonline")
@dataclass
class SharePointOnlineMapping(StreamConfig_Mapping):
    """SharePoint Online data provider mapping."""

    data_provider_type: str = "sharepointonline"
    src_url: str = "relativeURL"
