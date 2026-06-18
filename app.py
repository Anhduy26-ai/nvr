import asyncio
import aiohttp
import hashlib
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

NVR_IP = os.environ['NVR_IP']
NVR_USER = os.environ['NVR_USER']
NVR_PASS = os.environ['NVR_PASS']
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8080))), H).serve_forever(), daemon=True).start()

lh = {}
la = {}

async def main():
    global lh, la
    
    async with aiohttp.ClientSession() as s:
        try:
            await s.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                        json={'chat_id': CHAT_ID, 'text': '🟢 Monitor started'})
        except: pass
        
        while True:
            for ch in range(1, 5):
                try:
                    url = f'http://{NVR_IP}/cgi-bin/snapshot.cgi?channel={ch}'
                    auth = aiohttp.BasicAuth(NVR_USER, NVR_PASS)
                    
                    async with s.get(url, auth=auth, timeout=5) as r:
                        if r.status == 200:
                            img = await r.read()
                            h = hashlib.md5(img).hexdigest()
                            
                            if ch in lh and lh[ch] != h:
                                now = datetime.now()
                                if ch not in la or (now - la[ch]).total_seconds() > 10:
                                    form = aiohttp.FormData()
                                    form.add_field('chat_id', CHAT_ID)
                                    form.add_field('photo', img, filename=f'cam{ch}.jpg')
                                    form.add_field('caption', f'🚨 Chuyen dong cam {ch}\n🕒 {now.strftime("%H:%M:%S")}')
                                    await s.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', data=form)
                                    la[ch] = now
                            
                            lh[ch] = h
                except: pass
            
            await asyncio.sleep(0.5)

asyncio.run(main())
