"""Device manager: loads device classes, starts/stops them, and routes commands."""
import json
import logging
from typing import Dict

from backend.core.mqtt_client import MQTTClient
from backend.devices import (
    LampDevice,
    ThermostatDevice,
    CameraFrontDevice,
    CameraBackDevice,
    CameraSideDevice,
    SmartGateDevice,
    TVDevice,
    ACDevice,
)

logger = logging.getLogger("device_manager")

DEVICE_CLASS_MAP = {
    "lamp": LampDevice,
    "thermostat": ThermostatDevice,
    "camera_front": CameraFrontDevice,
    "camera_back": CameraBackDevice,
    "camera_side": CameraSideDevice,
    "smart_gate": SmartGateDevice,
    "tv": TVDevice,
    "ac": ACDevice,
}

class DeviceManager:
    def __init__(self, mqtt_client: MQTTClient, devices_config: dict):
        self.mqtt = mqtt_client
        self.devices_config = devices_config or {}
        self.devices: Dict[str, object] = {}

    def load_devices(self):
        for entry in self.devices_config.get("devices", []):
            device_id = entry.get("id")
            dtype = entry.get("type")
            cls = DEVICE_CLASS_MAP.get(dtype)
            if not cls:
                logger.warning("Unknown device type %s for %s", dtype, device_id)
                continue
            try:
                device = cls(device_id=device_id, mqtt_client=self.mqtt, meta=entry)
                self.devices[device_id] = device
            except Exception:
                logger.exception("Failed to instantiate device %s", device_id)

    def start_all(self):
        # Ensure MQTT connected
        if not self.mqtt.is_connected():
            ok = self.mqtt.connect()
            if not ok:
                logger.warning("MQTT client not connected; device threads may fail to subscribe until connection is ready")
        for d in self.devices.values():
            try:
                d.start()
            except Exception:
                logger.exception("Failed to start device %s", getattr(d, 'device_id', '<unknown>'))

    def stop_all(self):
        for d in self.devices.values():
            try:
                d.stop()
            except Exception:
                logger.exception("Error stopping device %s", getattr(d, 'device_id', '<unknown>'))
        self.mqtt.disconnect()

    def list_devices(self):
        out = []
        for did, d in self.devices.items():
            state = getattr(d, "last_state", None)
            out.append({"id": did, "type": getattr(d, "device_type", None), "state": state})
        return out

    def send_command(self, device_id: str, action: str, params: dict = None):
        params = params or {}
        device = self.devices.get(device_id)
        if not device:
            raise KeyError(device_id)
        # call device helper or publish to its MQTT topic
        return device.handle_action(action, params)
