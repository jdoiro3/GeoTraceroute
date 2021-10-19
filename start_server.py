import aiohttp
from aiohttp import web, WSCloseCode
import asyncio
import webbrowser
import json
import subprocess
import requests


HOST = "127.0.0.1"
PORT = 8888


async def http_handler(request):
    return web.FileResponse('./index.html')


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str('some websocket message payload')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())

    return ws


async def traceroute(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    msg = await ws.receive()
    if msg.type == aiohttp.WSMsgType.TEXT:
        data = json.loads(msg.data)["data"]
        host = data["host"]
        ip_info_tk = data["token"]

        with subprocess.Popen(["traceroute", "-I", "--max-hop=30", host], stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as process:
            for i, line in enumerate(process.stdout):
                if i == 0:
                    line_type = "input"
                else:
                    line_type = "output"
                terminal_msg = json.dumps({"type": line_type, "msg": line})
                await ws.send_str(terminal_msg)
                line_split = line.strip().split("  ")
                hop = line_split[0]
                ip_and_times_list = [val.strip() for val in line_split[1:]]
                try:
                    index = ip_and_times_list.index(next(filter(lambda x: x != "*", ip_and_times_list)))
                    ip = ip_and_times_list[index]
                except StopIteration:
                    ip = None
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