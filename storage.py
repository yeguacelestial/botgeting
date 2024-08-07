import json
import os
import pickle

STORAGE_FILE = 'template_status.json'
CREDENTIALS_DIR = 'credentials'

def load_template_status():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_template_status(data):
    with open(STORAGE_FILE, 'w') as file:
        json.dump(data, file)

def load_user_credentials(chat_id):
    try:
        with open(f'{CREDENTIALS_DIR}/{chat_id}.pickle', 'rb') as token:
            creds = pickle.load(token)
        print(f"Loaded credentials for chat_id {chat_id}")
        return creds
    except (FileNotFoundError, IOError) as e:
        print(f"Error loading credentials for chat_id {chat_id}: {e}")
        return None

def save_user_credentials(chat_id, creds):
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR)
    with open(f'{CREDENTIALS_DIR}/{chat_id}.pickle', 'wb') as token:
        pickle.dump(creds, token)
    print(f"Saved credentials for chat_id {chat_id}")