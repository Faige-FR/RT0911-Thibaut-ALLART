import paho.mqtt.client as mqtt
import json, time

# Files
VEHICLE = "vehicle"
POSITIONS = "positions"
LIGHTS = "lights"
TOP = "top"
UT = "UT"   # Uppertester
UTRESP = "RESP"

# Variables globales
goFlag = False
utFlag = False
lightLst = ""
posLst = ""

# Fonctions callback pour les évènements MQTT
    # Inscription aux files
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT brokers")
        client.subscribe(VEHICLE)
        client.subscribe(POSITIONS)
        client.subscribe(LIGHTS)
        client.subscribe(TOP)
        client.subscribe(UT)
    else:
        print("Connection failed with error code " + str(rc))

    # Réception des messages
def on_message(client, userdata, msg):
    global goFlag
    global utFlag
    global lightLst
    global posLst

    print("Received message on TOPIC '" + msg.topic + "': " + str(msg.payload.decode()))
    if msg.topic == TOP:
        goFlag = True
    elif msg.topic == LIGHTS:
        lightLst = json.loads(msg.payload.decode())
    elif msg.topic == POSITIONS:
        posLst = json.loads(msg.payload.decode())
    elif msg.topic == UT:
        jsonMsg = json.loads(msg.payload.decode())
        
        if jsonMsg["id"] == 3 or jsonMsg["id"] == str(3) :
            utFlag = True

    # Déconnexion
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection")