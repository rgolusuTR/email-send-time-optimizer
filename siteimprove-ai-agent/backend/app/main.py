"""
FastAPI application for Siteimprove AI Agent
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import asyncio
from typing import List, Optional
import pandas as pd
from datetime import datetime
import os

from .config import settings
from .models.broken_link import (
    BrokenLink, BrokenLinksResponse, ScanRequest, 
    PromptRequest, PromptResponse, FilterRequest, ExportRequest
)
from .services.siteimprove_automation import SiteimproveAutomation
from .services.prompt_parser import PromptParser
from .websocket_manager import websocket_manager

# Global instances
automation = SiteimproveAutomation(websocket_manager)
parser = PromptParser()
cached_data: List[BrokenLink] = []
last_scan_time: Optional[datetime] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    os.makedirs(settings.screenshot_path, exist_ok=True)
    yield
    # Shutdown
    await automation.stop()

app = FastAPI(
    title="Siteimprove AI Agent",
    description="AI-powered automation for Siteimprove broken links management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Siteimprove AI Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/prompt", response_model=PromptResponse)
async def process_prompt(request: PromptRequest, background_tasks: BackgroundTasks):
    """
    Process natural language prompts and execute corresponding actions
    """
    try:
        # Parse the prompt
        parsed = parser.parse_prompt(request.prompt)
        intent = parsed["intent"]
        parameters = parsed["parameters"]
        actions = parsed["actions"]
        suggestions = parsed["suggestions"]
        
        response_data = None
        action_taken = None
        
        if intent == "help":
            return PromptResponse(
                success=True,
                message=parser.get_help_text(),
                action_taken="help_displayed",
                suggestions=[]
            )
        
        elif intent == "login":
            # Execute login in background
            background_tasks.add_task(execute_login)
            return PromptResponse(
                success=True,
                message="Logging in to Siteimprove... This may take a moment.",
                action_taken="login_initiated",
                suggestions=["Try: 'Show me broken links' after login completes"]
            )
        
        elif intent == "scan":
            # Execute scan
            try:
                broken_links = await get_broken_links_data(force_refresh=True)
                response_data = {
                    "broken_links": [link.dict() for link in broken_links],
                    "total_count": len(broken_links),
                    "scan_time": datetime.now().isoformat()
                }
                action_taken = "scan_completed"
                message = f"Found {len(broken_links)} pages with broken links"
                
            except Exception as e:
                return PromptResponse(
                    success=False,
                    message=f"Failed to scan for broken links: {str(e)}",
                    suggestions=["Try: 'Login to Siteimprove' first"]
                )
        
        elif intent == "filter":
            # Apply filters to cached data
            filtered_data = apply_filters(cached_data, parameters)
            response_data = {
                "broken_links": [link.dict() for link in filtered_data],
                "total_count": len(filtered_data),
                "filters_applied": parameters
            }
            action_taken = "filter_applied"
            message = f"Filtered to {len(filtered_data)} pages matching your criteria"
        
        elif intent == "export":
            # Generate export file
            export_format = parameters.get("format", "csv")
            filename = await generate_export(cached_data, export_format)
            response_data = {"export_file": filename}
            action_taken = "export_generated"
            message = f"Export generated: {filename}"
        
        elif intent == "analyze":
            # Perform analysis
            analysis = perform_analysis(cached_data)
            response_data = analysis
            action_taken = "analysis_completed"
            message = "Analysis completed successfully"
        
        else:
            # Default to scan
            broken_links = await get_broken_links_data()
            response_data = {
                "broken_links": [link.dict() for link in broken_links],
                "total_count": len(broken_links)
            }
            action_taken = "default_scan"
            message = f"Retrieved {len(broken_links)} broken link entries"
        
        return PromptResponse(
            success=True,
            message=message,
            data=response_data,
            action_taken=action_taken,
            suggestions=suggestions
        )
        
    except Exception as e:
        return PromptResponse(
            success=False,
            message=f"Error processing prompt: {str(e)}",
            suggestions=["Try: 'help' to see available commands"]
        )

@app.get("/api/broken-links", response_model=BrokenLinksResponse)
async def get_broken_links(force_refresh: bool = False):
    """Get broken links data"""
    try:
        broken_links = await get_broken_links_data(force_refresh)
        
        summary = {
            "total_pages": len(broken_links),
            "total_broken_links": sum(link.broken_links for link in broken_links),
            "total_clicks": sum(link.clicks for link in broken_links),
            "total_page_views": sum(link.page_views for link in broken_links),
            "avg_broken_links_per_page": sum(link.broken_links for link in broken_links) / len(broken_links) if broken_links else 0
        }
        
        return BrokenLinksResponse(
            data=broken_links,
            total_count=len(broken_links),
            scan_timestamp=last_scan_time or datetime.now(),
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan")
async def trigger_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Trigger a new scan"""
    background_tasks.add_task(execute_scan, request.force_refresh)
    return {"message": "Scan initiated", "status": "processing"}

@app.post("/api/filter")
async def filter_broken_links(request: FilterRequest):
    """Filter broken links data"""
    try:
        filtered_data = apply_filters(cached_data, request.dict())
        return {
            "data": [link.dict() for link in filtered_data],
            "total_count": len(filtered_data),
            "filters_applied": request.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export")
async def export_data(request: ExportRequest):
    """Export data to file"""
    try:
        data_to_export = cached_data
        if request.filters:
            data_to_export = apply_filters(cached_data, request.filters.dict())
        
        filename = await generate_export(data_to_export, request.format)
        return {"filename": filename, "download_url": f"/api/download/{filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download exported file"""
    file_path = f"./exports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and listen for any client messages
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket_manager.send_personal_message(
                {"type": "echo", "message": f"Received: {data}"}, 
                websocket
            )
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "logged_in": automation.logged_in,
        "last_scan": last_scan_time.isoformat() if last_scan_time else None,
        "cached_entries": len(cached_data),
        "browser_active": automation.browser is not None
    }

# Helper functions
async def get_broken_links_data(force_refresh: bool = False) -> List[BrokenLink]:
    """Get broken links data with caching"""
    global cached_data, last_scan_time
    
    if not force_refresh and cached_data and last_scan_time:
        # Check if cache is still valid
        cache_age = (datetime.now() - last_scan_time).total_seconds()
        if cache_age < settings.cache_duration:
            return cached_data
    
    # Fetch fresh data
    broken_links = await automation.get_broken_links_report(force_refresh)
    
    # Calculate priority scores
    for link in broken_links:
        link.priority_score = calculate_priority_score(link)
    
    # Update cache
    cached_data = broken_links
    last_scan_time = datetime.now()
    
    return broken_links

async def execute_login():
    """Execute login process with WebSocket updates"""
    try:
        success = await automation.login()
        if success:
            await websocket_manager.send_completion(
                "login", 
                "🎉 Login completed successfully! You can now scan for broken links.",
                {"logged_in": True}
            )
        else:
            await websocket_manager.send_error("Login failed. Please check your credentials.")
    except Exception as e:
        await websocket_manager.send_error(f"Login failed: {str(e)}")
        print(f"Login failed: {e}")

async def execute_scan(force_refresh: bool = False):
    """Execute scan process with WebSocket updates"""
    try:
        await websocket_manager.send_scan_step("start", "🔍 Starting broken links scan...")
        broken_links = await get_broken_links_data(force_refresh)
        await websocket_manager.send_completion(
            "scan",
            f"✅ Scan completed! Found {len(broken_links)} pages with broken links.",
            {"broken_links_count": len(broken_links)}
        )
    except Exception as e:
        await websocket_manager.send_error(f"Scan failed: {str(e)}")
        print(f"Scan failed: {e}")

def apply_filters(data: List[BrokenLink], filters: dict) -> List[BrokenLink]:
    """Apply filters to broken links data"""
    filtered_data = data.copy()
    
    for key, value in filters.items():
        if value is None:
            continue
            
        if key == "min_clicks":
            filtered_data = [link for link in filtered_data if link.clicks >= value]
        elif key == "max_clicks":
            filtered_data = [link for link in filtered_data if link.clicks <= value]
        elif key == "min_page_views":
            filtered_data = [link for link in filtered_data if link.page_views >= value]
        elif key == "max_page_views":
            filtered_data = [link for link in filtered_data if link.page_views <= value]
        elif key == "min_broken_links":
            filtered_data = [link for link in filtered_data if link.broken_links >= value]
        elif key == "max_broken_links":
            filtered_data = [link for link in filtered_data if link.broken_links <= value]
        elif key == "page_level":
            filtered_data = [link for link in filtered_data if link.page_level == value]
        elif key == "search_term":
            filtered_data = [link for link in filtered_data if value.lower() in link.title.lower() or value.lower() in link.url.lower()]
    
    return filtered_data

async def generate_export(data: List[BrokenLink], format_type: str) -> str:
    """Generate export file"""
    os.makedirs("./exports", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"broken_links_{timestamp}.{format_type}"
    filepath = f"./exports/{filename}"
    
    # Convert to DataFrame
    df = pd.DataFrame([link.dict() for link in data])
    
    if format_type == "csv":
        df.to_csv(filepath, index=False)
    elif format_type == "xlsx":
        df.to_excel(filepath, index=False)
    elif format_type == "json":
        df.to_json(filepath, orient="records", indent=2)
    
    return filename

def calculate_priority_score(link: BrokenLink) -> float:
    """Calculate priority score for a broken link"""
    # Simple scoring algorithm
    score = 0.0
    
    # Weight by number of broken links
    score += link.broken_links * 2.0
    
    # Weight by clicks (user engagement)
    score += link.clicks * 1.5
    
    # Weight by page views (visibility)
    score += link.page_views * 1.0
    
    # Weight by page level (higher level = more important)
    score += (5 - link.page_level) * 0.5 if link.page_level <= 5 else 0
    
    return round(score, 2)

def perform_analysis(data: List[BrokenLink]) -> dict:
    """Perform analysis on broken links data"""
    if not data:
        return {"message": "No data available for analysis"}
    
    # Sort by priority score
    sorted_data = sorted(data, key=lambda x: x.priority_score or 0, reverse=True)
    
    analysis = {
        "total_pages": len(data),
        "total_broken_links": sum(link.broken_links for link in data),
        "highest_priority": sorted_data[0].dict() if sorted_data else None,
        "top_5_critical": [link.dict() for link in sorted_data[:5]],
        "pages_by_level": {},
        "avg_broken_links": sum(link.broken_links for link in data) / len(data),
        "recommendations": []
    }
    
    # Group by page level
    for link in data:
        level = link.page_level
        if level not in analysis["pages_by_level"]:
            analysis["pages_by_level"][level] = 0
        analysis["pages_by_level"][level] += 1
    
    # Generate recommendations
    if analysis["highest_priority"]:
        analysis["recommendations"].append(f"Priority fix: {analysis['highest_priority']['title']}")
    
    high_traffic_broken = [link for link in data if link.clicks > 10 and link.broken_links > 2]
    if high_traffic_broken:
        analysis["recommendations"].append(f"Fix {len(high_traffic_broken)} high-traffic pages with multiple broken links")
    
    return analysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)
