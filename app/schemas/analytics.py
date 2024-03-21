from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

class Activity(BaseModel):
    type: Literal["click", "scan"]
    timestamp: str | datetime = Field(
        ...,
        title="Timestamp",
        description="The timestamp to get analytics for",
        examples=["2021-08-01T12:00:00Z"],
    )
    ip_address: str | None = Field(None, title="IP Address", description="The IP address of the click")
    browser: str | None = Field(None, title="Browser", description="The browser of the click")
    referer: str | None = Field(
        ...,
        title="Referer",
        description="The referer to get analytics for",
        examples=["https://example.com/"],
    )


class TimelineData(BaseModel):
    time_line: list[Activity]


class OverviewData(BaseModel):
    clicks: int
    scans: int
    total_engagement: int


class CountriesData(BaseModel):
    countries: dict[str, int]


class DeviceData(BaseModel):
    devices: dict[str, int]
