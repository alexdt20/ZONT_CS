import paho.mqtt.client as mqtt
import json
import re
import logging
import os
from typing import Optional, Dict, Any

# Настройка логирования - исправленные пути для Windows
LOG_DIR = os.path.join(os.environ['TEMP'], 'mqtt_bridge')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'mqtt_bridge.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# MQTT настройки
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
MQTT_USERNAME = "hass"  # Замените на ваше имя пользователя
MQTT_PASSWORD = "mqtt"  # Замените на ваш пароль
MQTT_TOPIC_STATE = "homeassistant/sensor/5EDB89AEDC88/+/state"
MQTT_TOPIC_CONFIG = "homeassistant/sensor/5EDB89AEDC88/+/config"
MQTT_TOPIC_COMMAND = "homed/command/custom"

# SSL настройки (если требуется)
MQTT_SSL = False
MQTT_SSL_CA_CERTS = None
MQTT_SSL_CERTFILE = None
MQTT_SSL_KEYFILE = None

# Словарь для хранения конфигураций устройств
devices_config: Dict[str, Dict[str, Any]] = {}

def on_connect(client, userdata, flags, rc):
    """Callback при подключении к MQTT брокеру"""
    if rc == 0:
        logging.info("Successfully connected to MQTT broker")
        # Подписываемся на топики
        client.subscribe(MQTT_TOPIC_STATE)
        client.subscribe(MQTT_TOPIC_CONFIG)
        logging.info(f"Subscribed to topics: {MQTT_TOPIC_STATE}, {MQTT_TOPIC_CONFIG}")
    else:
        error_messages = {
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorised"
        }
        error_msg = error_messages.get(rc, f"Connection failed with result code {rc}")
        logging.error(f"Failed to connect to MQTT broker: {error_msg}")

def on_disconnect(client, userdata, rc):
    """Callback при отключении от MQTT брокеру"""
    if rc != 0:
        logging.warning(f"Unexpected disconnection from MQTT broker (rc: {rc})")
    else:
        logging.info("Disconnected from MQTT broker")

def on_message(client, userdata, msg):
    """Callback при получении сообщения"""
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logging.debug(f"Received message on topic: {topic}")
        
        # Извлекаем ID устройства из топика
        device_id_match = re.search(r'homeassistant/sensor/5EDB89AEDC88/(\d+)/(state|config)', topic)
        if not device_id_match:
            logging.warning(f"Cannot extract device ID from topic: {topic}")
            return
            
        device_id = device_id_match.group(1)
        
        if topic.endswith('/config'):
            # Обрабатываем конфигурационное сообщение
            process_config_message(device_id, payload)
        elif topic.endswith('/state'):
            # Обрабатываем сообщение состояния
            process_state_message(device_id, payload)
            
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in message: {e}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")

def process_config_message(device_id: str, payload: str):
    """Обрабатываем конфигурационное сообщение"""
    try:
        config_data = json.loads(payload)
        devices_config[device_id] = {
            'name': config_data.get('name', f'Device_{device_id}'),
            'unit': config_data.get('unit_of_meas', '°C'),
            'value_template': config_data.get('val_tpl', '{{ value_json.t}}')
        }
        logging.info(f"Config stored for device {device_id}: {devices_config[device_id]['name']}")
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config: {e}")
    except Exception as e:
        logging.error(f"Error processing config for device {device_id}: {e}")

def process_state_message(device_id: str, payload: str):
    """Обрабатываем сообщение состояния"""
    try:
        state_data = json.loads(payload)
        
        # Проверяем, есть ли конфиг для этого устройства
        if device_id not in devices_config:
            logging.warning(f"No config found for device {device_id}")
            return
            
        # Создаем команду для homed
        command = create_homed_command(device_id, state_data)
        
        # Отправляем команду
        client.publish(MQTT_TOPIC_COMMAND, json.dumps(command), qos=1)
        logging.info(f"Command sent for device {device_id}: {command['data']['name']}")
        
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in state: {e}")
    except Exception as e:
        logging.error(f"Error processing state for device {device_id}: {e}")

def create_homed_command(device_id: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
    """Создает команду для homed на основе состояния устройства"""
    config = devices_config.get(device_id, {})
    
    command = {
        "action": "updateDevice",
        "data": {
            "active": True,
            "availabilityPattern": "",
            "availabilityTopic": "",
            "bindings": {
                "state": {
                    "inPattern": "{{ json.a }}",
                    "inTopic": f"homeassistant/sensor/5EDB89AEDC88/{device_id}/state"
                },
                "temperature": {
                    "inPattern": "{{ json.t }}",
                    "inTopic": f"homeassistant/sensor/5EDB89AEDC88/{device_id}/state"
                },
                "trig": {
                    "inPattern": "{{ json.trig }}",
                    "inTopic": f"homeassistant/sensor/5EDB89AEDC88/{device_id}/state"
                }
            },
            "cloud": False,
            "discovery": False,
            "exposes": ["temperature", "state", "trig"],
            "id": f"sensor_{device_id}",
            "name": config.get('name', f'Device_{device_id}'),
            "note": "",
            "options": {
                "state": {"type": "binary"},
                "trig": {"type": "binary"}
            },
            "real": True
        },
        "device": f"sensor_{device_id}"
    }
    
    return command

def setup_mqtt_client() -> mqtt.Client:
    """Настраивает и возвращает MQTT клиент"""
    client = mqtt.Client()
    
    # Устанавливаем callback функции
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    # Настраиваем авторизацию
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        logging.info("MQTT authentication configured")
    
    # Настраиваем SSL (если требуется)
    if MQTT_SSL:
        client.tls_set(
            ca_certs=MQTT_SSL_CA_CERTS,
            certfile=MQTT_SSL_CERTFILE,
            keyfile=MQTT_SSL_KEYFILE
        )
        logging.info("SSL/TLS configured")
    
    return client

def main():
    """Основная функция"""
    logging.info("Starting MQTT to HomEd bridge...")
    logging.info(f"Log file: {LOG_FILE}")
    
    try:
        # Создаем и настраиваем клиент
        global client
        client = setup_mqtt_client()
        
        # Подключаемся к брокеру
        logging.info(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Запускаем цикл обработки сообщений
        logging.info("Starting MQTT message loop...")
        client.loop_forever()
        
    except KeyboardInterrupt:
        logging.info("Received interrupt signal, shutting down...")
        client.disconnect()
    except Exception as e:
        logging.error(f"Failed to start MQTT bridge: {e}")
        raise

if __name__ == "__main__":
    main()