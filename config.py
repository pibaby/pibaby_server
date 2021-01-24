import yaml
import logging

# default values
conf = {
    "long_press": 1.2, # long press in seconds
    "delay": 1.0, # timer length before counting buttons
    "sleep_track_limit": 2 #seconds
}

def update_config(key, value):
    global conf
    if key == "sleep_track_limit":
        conf["sleep_track_limit"] = value
    elif key == "long_press":
        conf["long_press"] = value
    elif key == "delay":
        conf["delay"] = value
    else:
        logging.warn(f"update_config Setting Key: {key} not found")
    with open(r'./config.yaml', 'w') as file:
        yaml.dump(conf, file)

def read_config():
    global conf
    try:
        with open(r'./config.yaml') as file:
            values = yaml.load(file, Loader=yaml.FullLoader)
            for key, value in  values.items():
                conf[f"{key}"] = value
    except Exception as e:
        logging.debug("""No config file ./config.yaml
will create file on first update""")

