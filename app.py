# app.py
from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os, json

app = Flask(__name__)

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

DATA_FILE = 'data.json'

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/', methods=['GET'])
def home():
    return "<h1>JINX API JALAN!</h1><p>POST ke /send_code</p>"

@app.route('/send_code', methods=['POST'])
def send_code():
    phone = request.form.get('phone')
    if not phone:
        return jsonify({'success': False, 'error': 'no phone'})
    if not SESSION_STRING:
        return jsonify({'success': False, 'error': 'SESSION_STRING missing'})

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    client.connect()
    try:
        res = client.send_code_request(phone)
        client.disconnect()
        return jsonifyjsonify({'success': True, 'hash': res.phone_code_hash})
    except Exception as e:
        client.disconnect()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    code = request.form.get('code')
    hash_code = request.form.get('hash')
    if not all([phone, code, hash_code]):
        return jsonify({'success': False, 'error': 'missing'})

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    client.connect()
    try:
        client.sign_in(phone, code=code, phone_code_hash=hash_code)
        sess = client.session.save()
        data = load()
        data[phone] = {'session': sess}
        save(data)
        client.disconnect()
        return jsonify({'success': True, 'session': sess})
    except Exception as e:
        client.disconnect()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    app.run()
