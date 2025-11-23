from fastapi import APIRouter, WebSocket
import asyncio
from typing import Set

websocket_router = APIRouter()


class WebSocketManager:
    """Manage active WebSocket connections and allow thread-safe broadcasts."""
    def __init__(self):
        self.active: Set[WebSocket] = set()
        # running loop will be set when app starts; default to None
        self._loop = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        try:
            self.active.remove(websocket)
        except KeyError:
            pass

    async def _broadcast(self, message):
        dead = []
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            try:
                await ws.close()
            except Exception:
                pass
            try:
                self.active.remove(ws)
            except Exception:
                pass

    def broadcast(self, message):
        """Schedule a broadcast from any thread. Uses run_coroutine_threadsafe."""
        if not self._loop:
            return
        try:
            asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)
        except Exception:
            pass


@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # manager is attached to app state by main startup
    from fastapi import Request
    # In FastAPI websocket endpoints you can access app via websocket.app
    manager: WebSocketManager = websocket.app.state.get("ws_manager")
    if manager is None:
        # no manager available; accept and close
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "ws manager not available"})
        await websocket.close()
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Simple echo ack for incoming client messages
            await websocket.send_json({"type": "ack", "received": data})
    except Exception:
        pass
    finally:
        await manager.disconnect(websocket)

