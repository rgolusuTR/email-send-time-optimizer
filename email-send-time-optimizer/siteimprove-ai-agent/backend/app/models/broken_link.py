"""
Data models for broken links
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class BrokenLink(BaseModel):
    """Model for a broken link entry"""
    title: str = Field(..., description="Page title")
    url: str = Field(..., description="Page URL")
    broken_links: int = Field(..., description="Number of broken links on the page")
    clicks: int = Field(..., description="Number of clicks")
    page_level: int = Field(..., description="Page level in site hierarchy")
    page_views: int = Field(..., description="Number of page views")
    priority_score: Optional[float] = Field(None, description="AI-calculated priority score")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")

class BrokenLinksResponse(BaseModel):
    """Response model for broken links API"""
    data: List[BrokenLink]
    total_count: int
    scan_timestamp: datetime
    summary: dict

class ScanRequest(BaseModel):
    """Request model for triggering a scan"""
    force_refresh: bool = Field(False, description="Force a fresh scan ignoring cache")

class PromptRequest(BaseModel):
    """Request model for prompt-based commands"""
    prompt: str = Field(..., description="Natural language command")
    context: Optional[dict] = Field(None, description="Additional context for the command")

class PromptResponse(BaseModel):
    """Response model for prompt commands"""
    success: bool
    message: str
    data: Optional[dict] = None
    action_taken: Optional[str] = None
    suggestions: Optional[List[str]] = None

class FilterRequest(BaseModel):
    """Request model for filtering broken links"""
    min_clicks: Optional[int] = None
    max_clicks: Optional[int] = None
    min_page_views: Optional[int] = None
    max_page_views: Optional[int] = None
    min_broken_links: Optional[int] = None
    max_broken_links: Optional[int] = None
    page_level: Optional[int] = None
    search_term: Optional[str] = None

class ExportRequest(BaseModel):
    """Request model for data export"""
    format: str = Field("csv", description="Export format (csv, json, xlsx)")
    filters: Optional[FilterRequest] = None
    include_priority: bool = Field(True, description="Include priority scores in export")
