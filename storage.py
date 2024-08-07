import json
import os

STORAGE_FILE = 'template_status.json'

def load_template_status():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_template_status(data):
    with open(STORAGE_FILE, 'w') as file:
        json.dump(data, file)