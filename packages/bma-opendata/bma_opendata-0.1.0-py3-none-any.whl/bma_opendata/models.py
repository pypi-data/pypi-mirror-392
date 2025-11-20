"""Data models for the Bangkok Open Data CKAN SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    """Base model configuring shared validation behavior."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class BaseResponse(APIModel):
    """Common fields returned by CKAN action responses."""

    help: str
    success: bool


class ErrorInfo(APIModel):
    """Error payload returned when CKAN indicates success = False."""

    message: str
    error_type: Optional[str] = Field(default=None, alias="__type")


class Organization(APIModel):
    """Organization metadata embedded in dataset responses."""

    id: str
    name: str
    title: str
    description: Optional[str] = None
    created: datetime
    state: str
    is_organization: bool
    image_url: Optional[str] = None
    type: str
    approval_status: str


class Tag(APIModel):
    """Dataset tag metadata."""

    id: str
    name: str
    vocabulary_id: Optional[str] = None


class Group(APIModel):
    """Dataset group metadata."""

    id: str
    name: str
    title: Optional[str] = None
    description: Optional[str] = None
    created: Optional[datetime] = None
    is_group: Optional[bool] = None
    state: Optional[str] = None
    display_name: Optional[str] = None


class Resource(APIModel):
    """Resource metadata describing a downloadable file or service."""

    id: str
    resource_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    url: str
    format: str
    mimetype: Optional[str] = None
    size: Optional[int] = None
    created: datetime
    metadata_modified: datetime
    datastore_active: bool
    hash: Optional[str] = None
    package_id: str


class Dataset(APIModel):
    """Dataset (package) metadata definition."""

    id: str
    name: str
    title: str
    private: bool
    maintainer: Optional[str] = None
    maintainer_email: Optional[str] = None
    author: Optional[str] = None
    author_email: Optional[str] = None
    license_title: str
    license_id: str
    metadata_created: datetime
    metadata_modified: datetime
    organization: Optional[Organization] = None
    resources: list[Resource]
    tags: list[Tag] = Field(default_factory=list)
    groups: list[Group] = Field(default_factory=list)
    num_tags: Optional[int] = None
    version: Optional[str] = None
    state: Optional[str] = None


class SearchResult(APIModel):
    """Envelope describing package_search results."""

    count: int
    results: list[Dataset]
    sort: Optional[str] = None
    facets: Optional[dict[str, Any]] = None
    search_facets: Optional[dict[str, Any]] = None


class StringListResponse(BaseResponse):
    """Response containing a list of dataset identifiers."""

    result: list[str]


class DatasetResponse(BaseResponse):
    """Response containing a dataset object."""

    result: Dataset


class ResourceResponse(BaseResponse):
    """Response containing a resource object."""

    result: Resource


class SearchResponse(BaseResponse):
    """Response containing dataset search results."""

    result: SearchResult


class HelpResponse(BaseResponse):
    """Response containing help text or action listings."""

    result: str


class ErrorResponse(BaseResponse):
    """Response returned by CKAN when a request fails."""

    error: ErrorInfo


__all__ = [
    "APIModel",
    "BaseResponse",
    "Dataset",
    "DatasetResponse",
    "ErrorInfo",
    "ErrorResponse",
    "Group",
    "HelpResponse",
    "Organization",
    "Resource",
    "ResourceResponse",
    "SearchResponse",
    "SearchResult",
    "StringListResponse",
    "Tag",
]
