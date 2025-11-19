"""Domo stream configuration mappings."""

from dataclasses import dataclass

from ..stream_config import StreamConfig_Mapping, register_mapping

__all__ = [
    "DatasetCopyMapping",
    "DomoCSVMapping",
]


@register_mapping("dataset-copy")
@dataclass
class DatasetCopyMapping(StreamConfig_Mapping):
    """Dataset copy data provider mapping."""

    data_provider_type: str = "dataset-copy"
    src_url: str = "datasourceUrl"


@register_mapping("domo-csv")
@dataclass
class DomoCSVMapping(StreamConfig_Mapping):
    """Domo CSV data provider mapping."""

    data_provider_type: str = "domo-csv"
    src_url: str = "datasourceUrl"
