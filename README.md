# RT0911-Thibaut-ALLART
Projet de RT9011 - Test et vérification

# Installation
Installer les packages Python nécessaires au bon fonctionnement du programme s'ils ne le sont pas :
- paho.mqtt.client ;
- random ;
- configparser ;
- json ;
- time.

# Utilisation des codes
Les fichiers Python doivent être situés dans le même dossier.
Pour démarrer le programme, il faut lancer le script "main.py" avec la commande "python main.py" (remplacer "python" par "python3" selon le package installé).

Si besoin de générer certaines informations, on peut lancer les scripts suivants de la même manière que le fichier principal :
- 'generateLights.py' => Génère un état dans chaque direction pour chaque feu de circulation ;
- 'go.py' => Envoi un signal "GO" dans la file "top" pour que les véhicules puissent démarrer ;
- 'senderRequestUT.py' => Génère un message dans la file "UT" qui demandera au véhicule ayant pour identifiant "3" de répondre dans la file "RESP"