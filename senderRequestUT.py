import paho.mqtt.client as mqtt
import time
import json

def on_connect(client, userdata, flags, rc):
    print("Connecté avec le code de retour : " + str(rc))

def on_disconnect(client, userdata, rc):
    print("Déconnexion du broker MQTT")

# Configuration du client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Connexion au broker MQTT
broker_address = "194.57.103.203"
port = 1883
client.connect(broker_address, port, keepalive=60)


while True:
    # Envoi d'une demande de l'uppertester au véhicule d'ID "3"
    MESSAGE = json.dumps({"id": 3})
    client.publish("UT", MESSAGE)
    time.sleep(30)

# Déconnexion du broker MQTT
client.disconnect()
