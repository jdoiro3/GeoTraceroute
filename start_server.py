import aiohttp
from aiohttp import web, WSCloseCode
import asyncio
import webbrowser
import json
import subprocess
import requests
import re
import sys


HOST = "127.0.0.1"
PORT = 8888
IP_PATTERN = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

def get_terminal_line(line, line_num):
    if line_num == 0:
        line_type = "input"
    else:
        line_type = "output"
    return json.dumps({"type": line_type, "msg": line})

def get_ip_from_line(line, line_num):
    if line_num != 0:
        ip = IP_PATTERN.search(line)
        if ip:
            return ip[0]
        return None
    else:
        return None

async def http_handler(request):
    return web.FileResponse('./index.html')


async def traceroute(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    msg = await ws.receive()

    if msg.type == aiohttp.WSMsgType.TEXT:

        data = json.loads(msg.data)["data"]
        host = data["host"]
        ip_info_tk = data["token"]

        if sys.platform.startswith('linux'):
            command = ["traceroute", "-I", "--max-hop=30", host]
        elif sys.platform.startswith('win32'):
            command = ["tracert", "-h", "30", host]

        with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as process:
            for i, line in enumerate(process.stdout):
                await ws.send_str(get_terminal_line(line, i))
                ip = get_ip_from_line(line, i)
                if ip:
                    ip_geolocation_data = requests.get(f"https://ipinfo.io/{ip}?token={ip_info_tk}").json()
                    geoloc_msg = json.dumps({"type": "geo", "msg": ip_geolocation_data})
                    await ws.send_str(geoloc_msg)

    elif msg.type == aiohttp.WSMsgType.ERROR:

        print('ws connection closed with exception %s' % ws.exception())



def create_runner():
    app = web.Application()
    app.add_routes([
        web.get('/',   http_handler),
        web.get('/ws', traceroute),
    ])
    app.router.add_static('/css/', path='static/css', name='css')
    app.router.add_static('/scripts/', path='static/scripts', name='scripts')
    return web.AppRunner(app)


async def start_server(host=HOST, port=PORT):
    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()


if __name__ == "__main__":
    webbrowser.open_new(f"http://localhost:{PORT}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()