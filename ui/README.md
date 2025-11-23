 # UI (React)

This folder contains a minimal React single-page application used to control and monitor devices.

Quickstart (development)

```bash
cd /home/aryo/projek-sistem-terdistribusi/projek-sistem-terdistribusi/ui
npm install
# optionally add proxy to backend in package.json: "proxy": "http://127.0.0.1:8000"
npm start
# open http://localhost:3000
```

Files of interest

- `src/App.jsx` - app root and polling logic
- `src/components/` - device cards and controls (DeviceList, DeviceCard, GateControl, CameraView)
- `src/services/api.js` - wrapper for REST calls
- `src/styles.css` - app styling

Notes

- The UI uses REST (`/api/devices`, `/api/device/control`) to interact with the backend. For development, add a `proxy` entry to `ui/package.json` so the dev server forwards API requests to the backend without CORS.
- The UI currently polls `/api/devices` every 5s. If you want real-time UI updates, I can add WebSocket support and a backend MQTT→WS broadcaster.

*** End Patch