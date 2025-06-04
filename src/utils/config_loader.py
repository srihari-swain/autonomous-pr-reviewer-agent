import json

BASE_CONFIG_DATA = None

def read_base_config(config_path="src/configs/config.json"):
    """
    Loads the config from the given path only once and returns it as a dictionary.
    """
    global BASE_CONFIG_DATA

    if BASE_CONFIG_DATA is None:
        with open(config_path, "r") as json_file:
            BASE_CONFIG_DATA = json.load(json_file)
    return BASE_CONFIG_DATA