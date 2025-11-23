"""AC device template."""
import logging
from backend.core.threads import DeviceThread

logger = logging.getLogger("device.ac")

class ACDevice(DeviceThread):
    device_type = "ac"

    def __init__(self, device_id: str, mqtt_client, meta: dict = None):
        super().__init__(device_id)
        self.mqtt = mqtt_client
        self.meta = meta or {}
        self.cmd_topic = f"home/ac/{device_id}/cmd"
        self.telemetry_topic = f"home/ac/{device_id}/telemetry"
        self.last_state = {"current_temp": 26.5, "target_temp": 24.0, "mode": "cool"}

    def start(self):
        self.mqtt.add_message_callback(self._on_mqtt_message)
        self.mqtt.subscribe(self.cmd_topic)
        super().start()

    def handle_action(self, action: str, params: dict = None):
        self.mqtt.publish(self.cmd_topic, {"action": action, "params": params or {}})
        return {"status": "sent"}

    def _on_mqtt_message(self, topic, payload):
        if topic == self.cmd_topic and isinstance(payload, dict):
            action = payload.get("action")
            params = payload.get("params", {})
            if action == "set_temp":
                self.last_state["target_temp"] = float(params.get("target_temp", self.last_state["target_temp"]))
            self.mqtt.publish(self.telemetry_topic, {"state": self.last_state})

    def run(self):
        while not self.stopped():
            try:
                self.mqtt.publish(self.telemetry_topic, {"state": self.last_state})
            except Exception:
                logger.exception("ac telemetry publish failed")
            self.sleep(45)
