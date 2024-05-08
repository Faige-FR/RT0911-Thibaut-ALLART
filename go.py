import paho.mqtt.client as mqtt
import time

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
    # Publication du message "GO" dans la file "TOP"
    client.publish("top", "GO")
    time.sleep(10)

# Déconnexion du broker MQTT
client.disconnect()
