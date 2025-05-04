# edge_emulator.py
import json
import time
import paho.mqtt.publish as publish

MQTT_HOST = "localhost"  # або "mqtt", якщо всередині Docker
MQTT_PORT = 1883
MQTT_TOPIC = "processed_data_topic"

data_list = [
    {
        "road_state": "smooth",
        "agent_data": {
            "accelerometer": { "x": 0.1, "y": 0.2, "z": 0.3 },
            "gps": { "latitude": 50.45, "longitude": 30.52 },
            "timestamp": "2025-05-04T10:00:00"
        }
    },
    {
        "road_state": "cracked",
        "agent_data": {
            "accelerometer": { "x": 0.4, "y": 0.1, "z": 0.6 },
            "gps": { "latitude": 50.46, "longitude": 30.53 },
            "timestamp": "2025-05-04T10:01:00"
        }
    },
    {
        "road_state": "hole",
        "agent_data": {
            "accelerometer": { "x": 1.0, "y": 1.1, "z": 1.2 },
            "gps": { "latitude": 50.47, "longitude": 30.54 },
            "timestamp": "2025-05-04T10:02:00"
        }
    }
]

for item in data_list:
    publish.single(
        topic=MQTT_TOPIC,
        payload=json.dumps(item),
        hostname=MQTT_HOST,
        port=MQTT_PORT
    )
    print(f"✅ Надіслано: {item['road_state']}")
    time.sleep(1)
