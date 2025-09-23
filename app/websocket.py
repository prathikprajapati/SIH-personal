"""
WebSocket Server for Real-time Updates
Handles real-time communication between server and clients
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_info: Dict[websockets.WebSocketServerProtocol, Dict] = {}

    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new client connection"""
        self.connected_clients.add(websocket)
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        self.client_info[websocket] = {
            "ip": client_ip,
            "connected_at": datetime.now().isoformat(),
            "user_agent": websocket.request_headers.get("User-Agent", "unknown")
        }

        logger.info(f"Client connected: {client_ip}")
        await self.broadcast_system_status()

    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a client connection"""
        if websocket in self.connected_clients:
            self.connected_clients.remove(websocket)
            client_info = self.client_info.pop(websocket, {})
            logger.info(f"Client disconnected: {client_info.get('ip', 'unknown')}")
            await self.broadcast_system_status()

    async def broadcast_system_status(self):
        """Broadcast current system status to all clients"""
        status_data = {
            "type": "system_status",
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "connected_clients": len(self.connected_clients),
                "total_connections": len(self.client_info)
            }
        }
        await self.broadcast(status_data)

    async def broadcast_device_update(self, device_id: str, status: str, progress: int = None):
        """Broadcast device status updates"""
        update_data = {
            "type": "device_update",
            "device_id": device_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

        if progress is not None:
            update_data["progress"] = progress

        await self.broadcast(update_data)

    async def broadcast_progress_update(self, progress: int, message: str):
        """Broadcast progress updates"""
        progress_data = {
            "type": "progress_update",
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(progress_data)

    async def broadcast_blockchain_update(self, action: str, certificate_id: str = None, data: dict = None):
        """Broadcast blockchain updates"""
        blockchain_data = {
            "type": "blockchain_update",
            "action": action,
            "timestamp": datetime.now().isoformat()
        }

        if certificate_id:
            blockchain_data["certificate_id"] = certificate_id

        if data:
            blockchain_data.update(data)

        await self.broadcast(blockchain_data)

    async def broadcast_notification(self, title: str, message: str, level: str = "info"):
        """Broadcast notifications to all clients"""
        notification_data = {
            "type": "notification",
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(notification_data)

    async def broadcast(self, data: dict):
        """Broadcast data to all connected clients"""
        if not self.connected_clients:
            return

        message = json.dumps(data)
        disconnected_clients = set()

        for websocket in self.connected_clients.copy():
            try:
                await websocket.send(message)
            except ConnectionClosed:
                disconnected_clients.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.add(websocket)

        # Clean up disconnected clients
        for websocket in disconnected_clients:
            await self.unregister_client(websocket)

    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle individual client connection"""
        await self.register_client(websocket)

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning("Received invalid JSON from client")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))
                except Exception as e:
                    logger.error(f"Error handling client message: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Internal server error"
                    }))

        except ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)

    async def handle_client_message(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle messages from clients"""
        message_type = data.get("type")

        if message_type == "ping":
            # Respond to ping with pong
            await websocket.send(json.dumps({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }))

        elif message_type == "subscribe":
            # Handle subscription requests
            channels = data.get("channels", [])
            logger.info(f"Client subscribed to channels: {channels}")

        elif message_type == "unsubscribe":
            # Handle unsubscription requests
            channels = data.get("channels", [])
            logger.info(f"Client unsubscribed from channels: {channels}")

        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def start_server(self, host: str = "localhost", port: int = 8765):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on {host}:{port}")

        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # Run forever

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# Convenience functions for broadcasting
async def broadcast_device_update(device_id: str, status: str, progress: int = None):
    """Convenience function to broadcast device updates"""
    await websocket_manager.broadcast_device_update(device_id, status, progress)

async def broadcast_progress_update(progress: int, message: str):
    """Convenience function to broadcast progress updates"""
    await websocket_manager.broadcast_progress_update(progress, message)

async def broadcast_blockchain_update(action: str, certificate_id: str = None, data: dict = None):
    """Convenience function to broadcast blockchain updates"""
    await websocket_manager.broadcast_blockchain_update(action, certificate_id, data)

async def broadcast_notification(title: str, message: str, level: str = "info"):
    """Convenience function to broadcast notifications"""
    await websocket_manager.broadcast_notification(title, message, level)

def get_websocket_manager():
    """Get the global WebSocket manager instance"""
    return websocket_manager
