"""TV device template."""
import logging
from backend.core.threads import DeviceThread

logger = logging.getLogger("device.tv")

class TVDevice(DeviceThread):
    device_type = "tv"

    def __init__(self, device_id: str, mqtt_client, meta: dict = None):
        super().__init__(device_id)
        self.mqtt = mqtt_client
        self.meta = meta or {}
        self.cmd_topic = f"home/tv/{device_id}/cmd"
        self.status_topic = f"home/tv/{device_id}/status"
        self.last_state = {"power": "off", "volume": 10, "input": "hdmi1"}

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
            if action == "power_on":
                self.last_state["power"] = "on"
            elif action == "power_off":
                self.last_state["power"] = "off"
            elif action == "set_volume":
                self.last_state["volume"] = int(params.get("value", self.last_state["volume"]))
            self.mqtt.publish(self.status_topic, {"state": self.last_state})

    def run(self):
        while not self.stopped():
            try:
                self.mqtt.publish(self.status_topic, {"state": self.last_state})
            except Exception:
                logger.exception("tv status publish failed")
            self.sleep(30)
