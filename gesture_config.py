import json
import os

CONFIG_FILE = "gestures_config.json"

def load_gesture_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_gesture_config(gestures_dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(gestures_dict, f, indent=4, ensure_ascii=False)
