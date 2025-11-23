# Backend

This backend is a FastAPI application that acts as an MQTT gateway between the UI and IoT devices.

Quickstart (dev):

1. Install dependencies (prefer a venv):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Backend — FastAPI + MQTT gateway

This folder contains the backend server: a FastAPI application that acts as an MQTT gateway and manages device threads.

What it contains
- `backend/api/` - FastAPI app entry, routes and WebSocket skeleton
- `backend/core/` - MQTT client wrapper, DeviceManager, thread utilities
- `backend/devices/` - per-device modules (one file per device type)
- `backend/config/` - `mqtt_config.json` and `devices_config.json`

Quickstart (development)

1. Create a Python virtual environment and install dependencies:

```bash
cd /home/aryo/projek-sistem-terdistribusi/projek-sistem-terdistribusi/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Ensure an MQTT broker is reachable (default: `localhost:1883`). See `backend/config/mqtt_config.json`.

3. Run the backend (from repo root) so the `backend` package imports work:

```bash
cd /home/aryo/projek-sistem-terdistribusi/projek-sistem-terdistribusi
source backend/.venv/bin/activate
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Developer notes
- On startup the FastAPI app loads `mqtt_config.json` and `devices_config.json`, creates an `MQTTClient`, instantiates `DeviceManager`, calls `load_devices()` and `start_all()`. On shutdown it calls `stop_all()`.
- Device modules implement a `DeviceThread` (in `backend/core/threads.py`), subscribe to their topics, and publish status/telemetry periodically.

Key files to modify when adding a new device
- `backend/config/devices_config.json` — add an entry for the device (id, type, name, any tokens)
- `backend/devices/<device>.py` — implement device-specific logic: `handle_action`, `_on_mqtt_message`, and `run()` loop

API endpoints
- `GET /api/devices` — list devices and last-known state
- `POST /api/device/control` — send a control action to a device (the backend routes this to DeviceManager)
- `GET /health` — returns service + MQTT connection status

MQTT behavior
- The backend uses `backend/core/mqtt_client.py` to connect to the broker and publish/subscribe.
- Topic conventions:
	- `home/{device_type}/{device_id}/cmd` - device commands
	- `home/{device_type}/{device_id}/status` - status/telemetry

If you need help wiring hardware to the device modules or adding command ACKs and real-time WebSocket broadcasts, I can implement those next.
