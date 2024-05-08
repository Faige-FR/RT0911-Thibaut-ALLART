import paho.mqtt.client as mqtt, random as rd, configparser as cp, json, time   # Python modules
import car, mqttClient  # Python files

# Fichier de la carte
MAP_FILEPATH = "carte.ini"

# Informations du message de départ
ID, vtype, start, end, direction, speed, trip_data = car.readIniFile("car.ini")
nbSteps = len(trip_data)
trip_data[nbSteps][2], trip_data[nbSteps][3] = end[0], end[1]   # Le dernier tronçon ne doit pas être entièrement parcouru, on s'arrête au point de destination
pos = start
current_trip_line = 1
finished = False

# Lecture des feux
config = cp.ConfigParser()
config.read(MAP_FILEPATH)
traffic_lights = []
for key in config['trafficLight']:
    x, y = map(int, config['trafficLight'][key].split(','))
    traffic_lights.append((int(key), x, y)) # Indices : 0 = ID du feu, 1 = x, 2 = y
countTrafficLights = len(traffic_lights)
print("Lights : ", traffic_lights)

# Files
VEHICLE = "vehicle"
POSITIONS = "positions"
LIGHTS = "lights"
TOP = "top"
UT = "UT"
UTRESP = "RESP"

# Boucle de traitement
try:
    # Paramétrage et connexion au broker MQTT
    client = mqtt.Client()
    client.on_connect = mqttClient.on_connect
    client.on_message = mqttClient.on_message
    client.on_disconnect = mqttClient.on_disconnect

    broker_address = "194.57.103.203"
    port = 1883
    client.connect(broker_address, port, keepalive=60)

    client.loop_start()
    time.sleep(0.1)

    # Positions de début et de fin de parcours
    print("Starting at: " + str(start))
    print("Ending at: " + str(end))
    print()

    # Attente du "GO"
    while not mqttClient.goFlag:
       time.sleep(0.1)

    # Affichage départ
    print("=== DEPART ===")
    print()

    while True:
        # Si le véhicule continue son trajet
        if direction < 4:
            MESSAGE = {"id": ID, "vtype": vtype, "x": pos[0], "y": pos[1], "dir": direction, "speed": speed}    # Format du message envoyé indiquant notre état et position
            MESSAGE = json.dumps(MESSAGE)

            # Envoi du message
            print("Sending: " + MESSAGE + " on '" + VEHICLE + "'")
            client.publish(VEHICLE, MESSAGE)
        
        # Délai avant chaque message
        time.sleep(1)
        
        # Changement possible de tronçon
        if not finished and pos[0] == trip_data[current_trip_line][2] and pos[1] == trip_data[current_trip_line][3]:
            if pos != end:
                current_trip_line += 1
            else:
                direction = 4
                finished = True
                print()
                print("=== ARRIVEE ===")
        
        # Recherche du prochain feu                
        nextLight = []
        lightIdx = 0
        while not nextLight and lightIdx < countTrafficLights - 1:
            if trip_data[current_trip_line][2] == traffic_lights[lightIdx][1] and trip_data[current_trip_line][3] == traffic_lights[lightIdx][2]:
                nextLight = traffic_lights[lightIdx]    # (ID, x, y)
            lightIdx += 1

        # Gestion des possibles collisions
        nbVehicles = len(mqttClient.posLst)
        maxDistAvailable = 999  # Si on risque de rentrer dans un véhicule, cette valeur représente le maximum que l'on peut parcourir
                                # ('999' par défaut puisque la taille de la map ne dépasse pas '100' en X et en Y)

        if direction <= 3 and direction >= 0 and nbVehicles > 0:
            for i in mqttClient.posLst: # On vérifie que chaque véhicule de la carte n'entrera pas en collision avec notre véhicule si l'on se rend au même endroit
                if i[direction] == direction:
                    if direction == 0 and pos[0] + min(int(speed), trip_data[current_trip_line][2] - pos[0]) >= i[x]:
                        maxDistAvailable = i[x] - pos[0] - 1
                    elif direction == 2 and pos[0] - min(int(speed), pos[0] - trip_data[current_trip_line][2]) <= i[x]:
                        maxDistAvailable = pos[0] - i[x] - 1
                    elif direction == 1 and pos[1] + min(int(speed), trip_data[current_trip_line][3] - pos[1]) == i[y]:
                        maxDistAvailable = i[y] - pos[1] - 1
                    elif direction == 1 and pos[1] - min(int(speed), pos[1] - trip_data[current_trip_line][3]) == i[y]:
                        maxDistAvailable = pos[1] - i[y] - 1
    
        # Déplacement
        """
        Direction entre 0 et 3 => Déplacement en cours
        Direction = 4 => Véhicule arrivé

        Pour chaque direction entre 0 et 3, on vérifie si on a reçu la position d'un feu :
        - S'il n'y en a pas, on considère que le feu est vert (pour faciliter le programme) ;
        - S'il y a un feu, on regarde son statut (rouge ou vert) ;
        - Si aucun message n'est reçu, on considère qu'un feu est rouge pour ne pas enfreindre le code de la route.

        Une fois l'état du prochain feu connu, on peut estimer la distance parcourable. Selon la direction, on vérifie qu'on ne dépasse pas un feu rouge. Si c'est le cas, on doit
        s'arrêter avant ce dernier. Sinon, on vérifie qu'on n'entrera pas en collision avec un véhicule proche. On calculera la distance parcourue en fonction de ces informations
        et de notre vitesse initiale.
        """
        if direction >= 0 and direction <= 3:
            if trip_data[current_trip_line][2] > pos[0]:
                direction = 0

                if nextLight == []:
                    nextLightStatus = 1 # Pas de feu dont équivalent à un "feu vert"
                elif mqttClient.lightLst and len(mqttClient.lightLst) > 0:
                    nextLightStatus = mqttClient.lightLst[str(nextLight[0])][direction]
                else:
                    nextLightStatus = 0 # Feu rouge si rien reçu

                if nextLight != [] and pos[0] + min(int(speed), trip_data[current_trip_line][2] - pos[0]) == nextLight[1] and nextLightStatus == 0:
                    pos[0] += min(maxDistAvailable, min(int(speed), trip_data[current_trip_line][2] - pos[0]) - 1)
                else:
                    pos[0] += min(maxDistAvailable, min(int(speed), trip_data[current_trip_line][2] - pos[0]))

            elif trip_data[current_trip_line][2] < pos[0]:
                direction = 2

                if nextLight == []:
                    nextLightStatus = 1 # Pas de feu dont équivalent à un "feu vert"
                elif mqttClient.lightLst and len(mqttClient.lightLst) > 0:
                    nextLightStatus = mqttClient.lightLst[str(nextLight[0])][direction]
                else:
                    nextLightStatus = 0 # Feu rouge si rien reçu

                if nextLight != [] and pos[0] - min(int(speed), pos[0] - trip_data[current_trip_line][2]) == nextLight[1] and nextLightStatus == 0:
                    pos[0] -= min(maxDistAvailable, min(int(speed), pos[0] - trip_data[current_trip_line][2]) - 1)
                else:
                    pos[0] -= min(maxDistAvailable, min(int(speed), pos[0] - trip_data[current_trip_line][2]))

            elif pos[1] < trip_data[current_trip_line][3]:
                direction = 1

                if nextLight == []:
                    nextLightStatus = 1 # Pas de feu dont équivalent à un "feu vert"
                elif mqttClient.lightLst and len(mqttClient.lightLst) > 0:
                    nextLightStatus = mqttClient.lightLst[str(nextLight[0])][direction]
                else:
                    nextLightStatus = 0 # Feu rouge si rien reçu

                if nextLight != [] and pos[1] + min(int(speed), trip_data[current_trip_line][3] - pos[1]) == nextLight[2] and nextLightStatus == 0:
                    pos[1] += min(maxDistAvailable, min(int(speed), trip_data[current_trip_line][3] - pos[1]) + 1)
                else:
                    pos[1] += min(maxDistAvailable, min(int(speed), trip_data[current_trip_line][3] - pos[1]))

            elif pos[1] > trip_data[current_trip_line][3]:
                direction = 3

                if nextLight == []:
                    nextLightStatus = 1 # Pas de feu dont équivalent à un "feu vert"
                elif mqttClient.lightLst and len(mqttClient.lightLst) > 0:
                    nextLightStatus = mqttClient.lightLst[str(nextLight[0])][direction]
                else:
                    nextLightStatus = 0 # Feu rouge si rien reçu

                if nextLight != [] and pos[1] - min(int(speed), pos[1] - trip_data[current_trip_line][3]) == nextLight[2] and nextLightStatus == 0:
                    pos[1] -= min(maxDistAvailable, min(int(speed), pos[1] - trip_data[current_trip_line][3]) - 1)
                else:
                    pos[1] -= min(maxDistAvailable, min(int(speed), pos[1] - trip_data[current_trip_line][3]))

            # Uppertester
            if mqttClient.utFlag:
                MESSAGE = json.dumps({"id": ID, "temps": int(time.time()), "position": str(pos[0]) + "," + str(pos[1])})

                print("Uppertester's request captured. Sending: " + MESSAGE + " on '" + UTRESP + "'")
                client.publish(UTRESP, MESSAGE)

                mqttClient.utFlag = False   # Réponse envoyée, on réinitialise le statut du flag pour ne pas envoyer un message non demandé

except KeyboardInterrupt:
    client.disconnect()
    client.loop_stop()