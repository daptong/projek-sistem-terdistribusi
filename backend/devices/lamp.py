"""Simple lamp device simulator/template.
Each device file should encapsulate device-specific logic and MQTT interactions.
"""
import json
import logging
import threading
from backend.core.threads import DeviceThread

logger = logging.getLogger("device.lamp")

class LampDevice(DeviceThread):
    device_type = "lamp"

    def __init__(self, device_id: str, mqtt_client, meta: dict = None):
        super().__init__(device_id)
        self.mqtt = mqtt_client
        self.meta = meta or {}
        self.last_state = {"power": "off", "brightness": 0}
        self.cmd_topic = f"home/lamp/{device_id}/cmd"
        self.status_topic = f"home/lamp/{device_id}/status"

    def start(self):
        # register callback and subscribe
        # use add_message_callback so multiple devices can register
        self.mqtt.add_message_callback(self._on_mqtt_message)
        self.mqtt.subscribe(self.cmd_topic)
        super().start()

    def handle_action(self, action: str, params: dict = None):
        params = params or {}
        payload = {"action": action, "params": params}
        self.mqtt.publish(self.cmd_topic, payload)
        return {"status": "sent", "topic": self.cmd_topic}

    def _on_mqtt_message(self, topic, payload):
        if topic == self.cmd_topic:
            # perform action and publish status
            try:
                action = payload.get("action") if isinstance(payload, dict) else None
                params = payload.get("params", {}) if isinstance(payload, dict) else {}
                if action == "on":
                    self.last_state.update({"power": "on"})
                elif action == "off":
                    self.last_state.update({"power": "off"})
                elif action == "set_brightness":
                    self.last_state["brightness"] = int(params.get("value", 0))
                # publish updated status
                self.mqtt.publish(self.status_topic, {"timestamp": "", "state": self.last_state})
            except Exception:
                logger.exception("Error handling lamp command")

    def run(self):
        # heartbeat/status publisher loop
        while not self.stopped():
            try:
                self.mqtt.publish(self.status_topic, {"timestamp": "", "state": self.last_state})
            except Exception:
                logger.exception("Failed to publish lamp status")
            self.sleep(30)
