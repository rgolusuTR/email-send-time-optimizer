"""
WebSocket manager for real-time updates during automation processes
"""
from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio
from loguru import logger

class WebSocketManager:
    """Manages WebSocket connections and broadcasts updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {"connected_at": asyncio.get_event_loop().time()}
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.connection_data:
                del self.connection_data[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected WebSocket clients"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_progress_update(self, step: str, message: str, progress: int = None, status: str = "in_progress"):
        """Send a progress update to all connected clients"""
        update = {
            "type": "progress_update",
            "step": step,
            "message": message,
            "status": status,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if progress is not None:
            update["progress"] = progress
        
        await self.broadcast(update)
        logger.info(f"Progress update sent: {step} - {message}")
    
    async def send_login_step(self, step: str, message: str, success: bool = True):
        """Send a login step update"""
        await self.send_progress_update(
            step=f"login_{step}",
            message=message,
            status="success" if success else "error"
        )
    
    async def send_scan_step(self, step: str, message: str, progress: int = None, success: bool = True):
        """Send a scan step update"""
        await self.send_progress_update(
            step=f"scan_{step}",
            message=message,
            progress=progress,
            status="success" if success else "error"
        )
    
    async def send_error(self, error_message: str, step: str = None):
        """Send an error message"""
        error_update = {
            "type": "error",
            "message": error_message,
            "step": step,
            "status": "error",
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(error_update)
    
    async def send_completion(self, action: str, message: str, data: dict = None):
        """Send a completion message"""
        completion_update = {
            "type": "completion",
            "action": action,
            "message": message,
            "status": "completed",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if data:
            completion_update["data"] = data
        
        await self.broadcast(completion_update)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
