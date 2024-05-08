import configparser as cp

def readIniFile(filepath = "car.ini"):
	# Lecture du fichier
	config = cp.ConfigParser()
	config.read(filepath)

	# Récupération des données
	ID = str(config['car']['id'])
	vtype = int(config['car']['vtype'])
	start = [int(value) for value in config['car']['start'].split(",")]
	end = [int(value) for value in config['car']['end'].split(",")]
	direction = int(config['car']['direction'])
	speed = int(config['car']['speed'])
	
	trip_data = {}
	for key, value in config['trip'].items():
		trip_data[int(key)] = list(map(int, value.split(',')))

	return ID, vtype, start, end, direction, speed, trip_data