"""Google stream configuration mappings."""

from dataclasses import dataclass

from ..stream_config import StreamConfig_Mapping, register_mapping

__all__ = [
    "GoogleSheetsMapping",
    "GoogleSpreadsheetsMapping",
]


@register_mapping("google-sheets")
@dataclass
class GoogleSheetsMapping(StreamConfig_Mapping):
    """Google Sheets data provider mapping."""

    data_provider_type: str = "google-sheets"
    google_sheets_file_name: str = "spreadsheetIDFileName"


@register_mapping("google-spreadsheets")
@dataclass
class GoogleSpreadsheetsMapping(StreamConfig_Mapping):
    """Google Spreadsheets data provider mapping."""

    data_provider_type: str = "google-spreadsheets"
    google_sheets_file_name: str = "spreadsheetIDFileName"
