"""
Simple echo http server
"""
import time
import os
import sys
from aiohttp import web

wait_time = float(sys.argv[1])
print(f'waiting {wait_time}')
time.sleep(wait_time)

PORT = os.environ['PORT']

routes = web.RouteTableDef()

@routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world")

app = web.Application()
app.add_routes(routes)
web.run_app(app, port=PORT)
