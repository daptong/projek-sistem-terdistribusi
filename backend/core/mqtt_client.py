"""Simple MQTT client wrapper using paho-mqtt.
This wrapper provides connect/subscribe/publish helpers and safe callback registration.
"""
import json
import threading
import logging
from typing import Callable

import paho.mqtt.client as mqtt

logger = logging.getLogger("mqtt_client")

class MQTTClient:
    def __init__(self, config: dict):
        self.config = config
        self.client = mqtt.Client(client_id=config.get("client_id"))
        user = config.get("username")
        password = config.get("password")
        if user:
            self.client.username_pw_set(user, password)
        # support multiple callbacks (devices can register their handlers)
        self._on_messages = []  # list of callables(topic, data)
        self._connected_ev = threading.Event()

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message_internal

        lwt = config.get("last_will")
        if lwt:
            topic = lwt.get("topic")
            payload = lwt.get("payload")
            qos = lwt.get("qos", 1)
            retain = lwt.get("retain", True)
            self.client.will_set(topic, payload=payload, qos=qos, retain=retain)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
            self._connected_ev.set()
        else:
            logger.warning("Failed to connect to MQTT broker, rc=%s", rc)

    def _on_disconnect(self, client, userdata, rc):
        logger.warning("MQTT disconnected, rc=%s", rc)
        self._connected_ev.clear()

    def _on_message_internal(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8")
            try:
                data = json.loads(payload)
            except Exception:
                data = payload
            # dispatch to all registered callbacks
            for cb in list(self._on_messages):
                try:
                    cb(msg.topic, data)
                except Exception:
                    logger.exception("Callback raised during MQTT message handling")
        except Exception:
            logger.exception("Error processing incoming MQTT message")

    def set_message_callback(self, callback: Callable[[str, object], None]):
        """Set a single callback (replaces existing callbacks)."""
        self._on_messages = [callback]

    def add_message_callback(self, callback: Callable[[str, object], None]):
        """Register an additional callback; callbacks receive (topic, data)."""
        self._on_messages.append(callback)

    def connect(self):
        host = self.config.get("broker", "localhost")
        port = int(self.config.get("port", 1883))
        keepalive = int(self.config.get("keepalive", 60))
        # TODO: TLS handling if needed
        self.client.connect_async(host, port, keepalive)
        self.client.loop_start()
        # wait for connection (with timeout)
        self._connected_ev.wait(timeout=10)
        return self._connected_ev.is_set()

    def disconnect(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            logger.exception("Error while disconnecting MQTT client")

    def publish(self, topic: str, payload, qos=1, retain=False):
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload)
        return self.client.publish(topic, payload=payload, qos=qos, retain=retain)

    def subscribe(self, topic: str, qos=1):
        return self.client.subscribe(topic, qos=qos)

    def is_connected(self) -> bool:
        return self._connected_ev.is_set()
