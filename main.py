import os
import RPi.GPIO as GPIO
import os.path
import logging
import sys
import time
import paho.mqtt.client as mqtt
from ruamel.yaml import YAML

CONFIG_PATH = os.path.join('./config.yaml')
config = YAML(typ='safe').load(open(CONFIG_PATH))

from src.rf_controller import RFController

logging.basicConfig(
  level=logging.INFO,
  format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

logger = logging.getLogger('mqtt2rf')

def prepare_client(rf_controller):
  mqtt_config = config['mqtt']
  client = mqtt.Client()

  client.enable_logger(logger)
  client.username_pw_set(mqtt_config['username'], mqtt_config['password'])

  def on_connect(client, userdata, flags, rc):
    rf_controller.setup(client)

  def on_message(client, userdata, msg):
    rf_controller.handle_message(msg)

  client.on_connect = on_connect
  client.on_message = on_message

  logger.info("Connecting to: " + mqtt_config['host'] + " at " + str(mqtt_config['port']))
  client.connect(mqtt_config['host'], mqtt_config['port'], 60)
  logger.info("Starting mqtt loop...")

  client.loop_start()
  return client

def main():
  logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
  )

  try:
    GPIO.setmode(GPIO.BCM)
    rf_controller = RFController(config['rf_switch'])
    client = prepare_client(rf_controller)
    while True:
      rf_controller.update()
      time.sleep(0.1)
  except KeyboardInterrupt:
    pass
  finally:
    rfdevice.cleanup()
    GPIO.cleanup()

if __name__ == '__main__':
  main()
