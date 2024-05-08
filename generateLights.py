import paho.mqtt.client as mqtt
import json
import random
import time

# Définition de la fonction pour générer une liste aléatoire de 0 et de 1
def generate_random_list(length):
    return [random.choice([0, 1]) for _ in range(length)]

# Fonction pour générer l'état des feux de circulation et envoyer un message JSON au topic MQTT
def send_message(num_elements = 29, topic = "lights"):   # Nombre de feux de circulation sur la carte // Nom de la file MQTT
    data = {}
    for i in range(1, num_elements + 1):
        data[i] = ','.join(map(str, generate_random_list(4)))   # Ajout de 4 éléments aléatoires valant 0 ou 1 dans le dictionnaire 'data'

    # Conversion du dictionnaire en JSON
    message = json.dumps(data)

    # Envoi du message
    client.publish(topic, message)
    print("Message JSON envoyé au topic MQTT :", message)

# Configuration du broker MQTT
broker_address = "194.57.103.203"  # Adresse du broker MQTT
port=1883	# Port du broker MQTT

# Connexion au broker MQTT et lancement de la boucle de traitement
client = mqtt.Client()
client.connect(broker_address, port=port, keepalive=60)
client.loop_start()

# Envoi périodique du message JSON toutes les 3 secondes
while True:
    send_message()
    time.sleep(3)
