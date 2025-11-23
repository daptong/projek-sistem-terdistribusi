"""FastAPI app entrypoint for the backend API and WS endpoints."""
from fastapi import FastAPI
from fastapi import Request
from .routes import router as api_router
from .ws import websocket_router, WebSocketManager
import asyncio

import json
from pathlib import Path
from backend.core.mqtt_client import MQTTClient
from backend.core.device_manager import DeviceManager

app = FastAPI(title="IoT Home Automation Backend")
app.include_router(api_router, prefix="/api")
app.include_router(websocket_router)


def _load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


@app.on_event("startup")
async def startup_event():
    # locate config files relative to this module
    base = Path(__file__).resolve().parents[1] / "config"
    mqtt_conf = _load_json(base / "mqtt_config.json")
    devices_conf = _load_json(base / "devices_config.json")

    # create mqtt client and device manager, store on app.state
    mqtt = MQTTClient(mqtt_conf)
    manager = DeviceManager(mqtt_client=mqtt, devices_config=devices_conf)
    # create websocket manager and attach running loop
    ws_manager = WebSocketManager()
    loop = asyncio.get_running_loop()
    ws_manager.set_event_loop(loop)
    app.state.ws_manager = ws_manager
    manager.load_devices()
    manager.start_all()
    app.state.device_manager = manager

    # broadcast incoming MQTT messages to connected WebSocket clients
    def _on_mqtt(topic, data):
        try:
            app.state.ws_manager.broadcast({"type": "mqtt", "topic": topic, "payload": data})
        except Exception:
            pass

    mqtt.add_message_callback(_on_mqtt)


@app.on_event("shutdown")
def shutdown_event():
    manager = getattr(app.state, "device_manager", None)
    if manager:
        manager.stop_all()


@app.get("/health")
async def health(request: Request):
    # reflect MQTT connection state if possible
    mgr = getattr(app.state, "device_manager", None)
    mqtt_ok = False
    if mgr and getattr(mgr, 'mqtt', None):
        try:
            mqtt_ok = mgr.mqtt.is_connected()
        except Exception:
            mqtt_ok = False
    return {"status": "ok", "mqtt_connected": mqtt_ok}
