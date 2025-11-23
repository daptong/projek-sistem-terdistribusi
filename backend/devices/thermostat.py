"""Thermostat device template."""
import logging
from backend.core.threads import DeviceThread

logger = logging.getLogger("device.thermostat")

class ThermostatDevice(DeviceThread):
    device_type = "thermostat"

    def __init__(self, device_id: str, mqtt_client, meta: dict = None):
        super().__init__(device_id)
        self.mqtt = mqtt_client
        self.meta = meta or {}
        self.last_state = {"current_temp": 22.0, "setpoint": 24.0, "mode": "auto"}
        self.cmd_topic = f"home/thermostat/{device_id}/cmd"
        self.telemetry_topic = f"home/thermostat/{device_id}/telemetry"

    def start(self):
        self.mqtt.add_message_callback(self._on_mqtt_message)
        self.mqtt.subscribe(self.cmd_topic)
        super().start()

    def handle_action(self, action: str, params: dict = None):
        params = params or {}
        payload = {"action": action, "params": params}
        self.mqtt.publish(self.cmd_topic, payload)
        return {"status": "sent"}

    def _on_mqtt_message(self, topic, payload):
        if topic == self.cmd_topic:
            if isinstance(payload, dict):
                action = payload.get("action")
                params = payload.get("params", {})
                if action == "set_temp":
                    self.last_state["setpoint"] = float(params.get("target_temp", self.last_state["setpoint"]))
                    self.mqtt.publish(self.telemetry_topic, {"state": self.last_state})

    def run(self):
        # publish telemetry periodically
        while not self.stopped():
            try:
                self.mqtt.publish(self.telemetry_topic, {"state": self.last_state})
            except Exception:
                logger.exception("Thermostat telemetry publish failed")
            self.sleep(60)
