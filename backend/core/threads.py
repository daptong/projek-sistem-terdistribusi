import threading
import time

class DeviceThread(threading.Thread):
    """Base class for device threads. Implements start/stop and heartbeat helper."""
    def __init__(self, device_id: str, stop_event: threading.Event = None):
        super().__init__(daemon=True)
        self.device_id = device_id
        self._stop_event = stop_event or threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        raise NotImplementedError("run must be implemented by device subclasses")

    def sleep(self, seconds: float):
        # sleep in small increments to be responsive to stop
        end = time.time() + seconds
        while time.time() < end and not self.stopped():
            time.sleep(min(0.5, end - time.time()))
