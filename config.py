import yaml
import logging
from os import walk
import json
import noise

# default values
conf = {
    "long_press": 1.2, # long press in seconds
    "delay": 1.0, # timer length before counting buttons
    "sleep_track_limit": 1, #minutes
    "selected_noise": "nature.wav",
    "available_noises":[],
    "volume_offset":0
}

def update_config(settings):
    global conf
    result = {"action":"success","message":f"Settings have been updated"}
    new_settings = conf

    for key, value in settings.items():
        try:
            new_settings[key] = value
        except Exception as e:
            error = f"update_config Setting Key: {key} not found {e}"
            logging.warn(error)
            result = {"action":"error","message": error}
    if result['action'] == "success":
        with open(r'./config.yaml', 'w') as file:
            yaml.dump(new_settings, file)
        read_config()
    noise.intialize_noise(conf['selected_noise'], conf['volume_offset'])
    return json.dumps(result)

def read_config():
    global white_noise
    global conf
    try:
        with open(r'./config.yaml') as file:
            values = yaml.load(file, Loader=yaml.FullLoader)
            for key, value in  values.items():
                conf[f"{key}"] = value
        _, _, conf['available_noises'] = next(walk("./noise/"))
    except Exception as e:
        logging.debug("""./config.yaml not found. creating from default values""")
        with open(r'./config.yaml', 'w') as file:
            yaml.dump(conf, file)
    print(conf)
    return conf

