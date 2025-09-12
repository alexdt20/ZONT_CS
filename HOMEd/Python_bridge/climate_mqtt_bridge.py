import paho.mqtt.client as mqtt
import json
import re
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# MQTT настройки
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
MQTT_USERNAME = "hass"
MQTT_PASSWORD = "mqtt"
MQTT_TOPIC_STATE = "homeassistant/climate/5EDB89AEDC88/+/state"
MQTT_TOPIC_CONFIG = "homeassistant/climate/5EDB89AEDC88/+/config"
MQTT_TOPIC_COMMAND = "homed/command/custom"

# Словарь для хранения конфигураций устройств
devices_config = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC_STATE)
        client.subscribe(MQTT_TOPIC_CONFIG)
        logging.info(f"Subscribed to: {MQTT_TOPIC_STATE}, {MQTT_TOPIC_CONFIG}")
    else:
        logging.error(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logging.debug(f"Received message on topic: {topic}")
        
        # Извлекаем ID устройства
        device_id_match = re.search(r'homeassistant/climate/5EDB89AEDC88/(\d+)/(state|config)', topic)
        if not device_id_match:
            return
            
        device_id = device_id_match.group(1)
        
        if topic.endswith('/config'):
            process_config_message(device_id, payload)
        elif topic.endswith('/state'):
            process_state_message(client, device_id, payload)
            
    except Exception as e:
        logging.error(f"Error processing message: {e}")

def process_config_message(device_id, payload):
    """Обрабатываем конфигурационное сообщение"""
    try:
        config_data = json.loads(payload)
        devices_config[device_id] = {
            'name': config_data.get('name', f'Climate_{device_id}'),
            'min_temp': config_data.get('min_temp', 5),
            'max_temp': config_data.get('max_temp', 80),
            'modes': config_data.get('modes', ['heat', 'off'])
        }
        logging.info(f"Config stored for climate device {device_id}: {devices_config[device_id]['name']}")
        
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config: {e}")

def process_state_message(client, device_id, payload):
    """Обрабатываем сообщение состояния и отправляем команду"""
    try:
        state_data = json.loads(payload)
        
        # Проверяем, есть ли конфиг для этого устройства
        if device_id not in devices_config:
            logging.warning(f"No config found for climate device {device_id}")
            return
        
        config = devices_config[device_id]
        
        # Создаем команду для HomEd
        command = create_homed_command(device_id, config, state_data)
        
        # Отправляем команду
        client.publish(MQTT_TOPIC_COMMAND, json.dumps(command), qos=1)
        logging.info(f"Climate command sent for device {device_id}: {command['data']['name']}")
        
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in state: {e}")
    except Exception as e:
        logging.error(f"Error processing state for device {device_id}: {e}")

def create_homed_command(device_id, config, state_data):
    """Создает команду для homed на основе состояния climate устройства"""
    
    # Определяем доступные режимы системы
    system_modes = []
    if "heat" in config.get('modes', []):
        system_modes.append("heat")
    if "cool" in config.get('modes', []):
        system_modes.append("cool")
    if "off" in config.get('modes', []):
        system_modes.append("off")
    if "auto" in config.get('modes', []):
        system_modes.append("auto")
    if "dry" in config.get('modes', []):
        system_modes.append("dry")
    if "fan" in config.get('modes', []):
        system_modes.append("fan")
    
    # Если нет режимов, добавляем стандартные
    if not system_modes:
        system_modes = ["off", "heat"]
    
    command = {
        "action": "updateDevice",
        "data": {
            "active": True,
            "availabilityPattern": "",
            "availabilityTopic": "",
            "bindings": {
                "temperature": {
                    "inPattern": "{{ json.c }}",
                    "inTopic": f"homeassistant/climate/5EDB89AEDC88/{device_id}/state"
                },
                "targetTemperature": {
                    "inPattern": "{{ json.s }}",
                    "inTopic": f"homeassistant/climate/5EDB89AEDC88/{device_id}/state"
                },
                "fault": {
                    "inPattern": "{{ json.f }}",
                    "inTopic": f"homeassistant/climate/5EDB89AEDC88/{device_id}/state"
                },
                "systemMode": {
                    "inPattern": "{{ json.m }}",
                    "inTopic": f"homeassistant/climate/5EDB89AEDC88/{device_id}/state"
                },
                "mode_id": {
                    "inPattern": "{{ json.m_id }}",
                    "inTopic": f"homeassistant/climate/5EDB89AEDC88/{device_id}/state"
                }
            },
            "cloud": False,
            "discovery": False,
            "exposes": [
                "thermostat",
                "fail",
                "mode_id",
                "mode",
                "fault"
            ],
            "id": f"climate_{device_id}",
            "name": config['name'],
            "note": "",
            "options": {
                "systemMode": {
                    "enum": system_modes
                },
                "targetTemperature": {
                    "min": config.get('min_temp', 5),
                    "max": config.get('max_temp', 80)
                },
                "runningStatus": True
            },
            "real": True
        },
        "device": f"climate_{device_id}"
    }
    
    return command

def setup_mqtt_client():
    """Настраивает и возвращает MQTT клиент"""
    client = mqtt.Client()
    
    # Устанавливаем callback функции
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Настраиваем авторизацию
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        logging.info("MQTT authentication configured")
    
    return client

def main():
    """Основная функция"""
    logging.info("Starting MQTT Climate to HomEd bridge...")
    
    try:
        # Создаем и настраиваем клиент
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
