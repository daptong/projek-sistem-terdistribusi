"""Camera front device (event-only example)."""
import logging
from backend.core.threads import DeviceThread

logger = logging.getLogger("device.camera_front")

class CameraFrontDevice(DeviceThread):
    device_type = "camera"

    def __init__(self, device_id: str, mqtt_client, meta: dict = None):
        super().__init__(device_id)
        self.mqtt = mqtt_client
        self.meta = meta or {}
        self.status_topic = f"home/camera/{device_id}/status"
        self.event_topic = f"home/camera/{device_id}/event"
        self.cmd_topic = f"home/camera/{device_id}/cmd"

    def start(self):
        self.mqtt.add_message_callback(self._on_mqtt_message)
        self.mqtt.subscribe(self.cmd_topic)
        super().start()

    def handle_action(self, action: str, params: dict = None):
        self.mqtt.publish(self.cmd_topic, {"action": action, "params": params or {}})
        return {"status": "sent"}

    def _on_mqtt_message(self, topic, payload):
        # handle commands like start_stream/stop_stream
        if topic == self.cmd_topic:
            logger.info("Camera cmd received: %s", payload)

    def run(self):
        # send heartbeat/status periodically
        while not self.stopped():
            try:
                self.mqtt.publish(self.status_topic, {"online": True})
            except Exception:
                logger.exception("camera status publish failed")
            self.sleep(30)
