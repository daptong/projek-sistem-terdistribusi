"""Smart gate device - primary security device template."""
import logging
from backend.core.threads import DeviceThread

logger = logging.getLogger("device.smart_gate")

class SmartGateDevice(DeviceThread):
    device_type = "smart_gate"

    def __init__(self, device_id: str, mqtt_client, meta: dict = None):
        super().__init__(device_id)
        self.mqtt = mqtt_client
        self.meta = meta or {}
        self.status_topic = f"home/gate/{device_id}/status"
        self.cmd_topic = f"home/gate/{device_id}/cmd"
        self.alert_topic = f"home/gate/{device_id}/alert"
        self.last_state = {"position": "closed", "locked": True}

    def start(self):
        self.mqtt.add_message_callback(self._on_mqtt_message)
        self.mqtt.subscribe(self.cmd_topic)
        super().start()

    def handle_action(self, action: str, params: dict = None):
        params = params or {}
        # enforce simple auth example
        if action == "open" and params.get("auth_token") != self.meta.get("open_token"):
            self.mqtt.publish(self.alert_topic, {"event": "unauthorized_open_attempt", "by": params.get("user")})
            return {"status": "unauthorized"}
        self.mqtt.publish(self.cmd_topic, {"action": action, "params": params})
        return {"status": "sent"}

    def _on_mqtt_message(self, topic, payload):
        if topic == self.cmd_topic:
            # example: ack command by updating status
            action = payload.get("action") if isinstance(payload, dict) else None
            if action == "open":
                self.last_state.update({"position": "opening", "locked": False})
            elif action == "close":
                self.last_state.update({"position": "closed"})
            self.mqtt.publish(self.status_topic, {"state": self.last_state})

    def run(self):
        while not self.stopped():
            try:
                self.mqtt.publish(self.status_topic, {"state": self.last_state})
            except Exception:
                logger.exception("gate status publish failed")
            self.sleep(20)
