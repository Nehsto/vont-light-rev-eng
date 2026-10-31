import asyncio
import re
from pathlib import Path
from string import Template
from aiohttp import web
from vont import Lightbulb

MAC = "7C:DF:A1:A0:DA:C1"
UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
BULB = web.AppKey("bulb", Lightbulb)
COMMAND_LOCK = web.AppKey("command_lock", asyncio.Lock)
PAGE = Template(Path(__file__).with_name("controls.html").read_text())


async def bulb_connection(app):
    bulb = Lightbulb(MAC, UUID)
    app[BULB] = bulb
    app[COMMAND_LOCK] = asyncio.Lock()
    try:
        await bulb.connect()
        yield
    finally:
        if bulb.client.is_connected:
            await bulb.disconnect()


async def index(request):
    bulb = request.app[BULB]
    return web.Response(text=PAGE.substitute(
        power_label="Turn off" if bulb.power else "Turn on",
        power_status="On" if bulb.power else "Off",
        power_target=0 if bulb.power else 1,
        warm_label="On" if bulb.warm_mode else "Off",
        warm_checked=str(bulb.warm_mode).lower(),
        warm_target=0 if bulb.warm_mode else 1,
        brightness=bulb.brightness,
        color="#{:02x}{:02x}{:02x}".format(*bulb.color),
    ), content_type="text/html")


async def form_data(request):
    origin = request.headers.get("Origin")
    if origin and origin != f"{request.scheme}://{request.host}":
        raise web.HTTPForbidden()
    return await request.post()


async def set_power(request):
    data = await form_data(request)
    if data.get("on") not in ("0", "1"):
        raise web.HTTPBadRequest(text="Power must be 0 or 1")
    async with request.app[COMMAND_LOCK]:
        await request.app[BULB].set_power(data["on"] == "1")
    raise web.HTTPSeeOther("/")


async def set_warm(request):
    data = await form_data(request)
    if data.get("on") not in ("0", "1"):
        raise web.HTTPBadRequest(text="Warm light must be 0 or 1")
    async with request.app[COMMAND_LOCK]:
        await request.app[BULB].set_warm_mode(data["on"] == "1")
    raise web.HTTPSeeOther("/")


async def set_brightness(request):
    data = await form_data(request)
    try:
        value = int(data.get("brightness", ""))
    except ValueError:
        raise web.HTTPBadRequest(text="Brightness must be an integer")
    if not 0 <= value <= 100:
        raise web.HTTPBadRequest(text="Brightness must be between 0 and 100")
    async with request.app[COMMAND_LOCK]:
        await request.app[BULB].set_brightness(value)
    raise web.HTTPSeeOther("/")


async def set_color(request):
    data = await form_data(request)
    color = data.get("color", "")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise web.HTTPBadRequest(text="Color must be a six-digit hex color")
    rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    async with request.app[COMMAND_LOCK]:
        await request.app[BULB].set_color(*rgb)
    raise web.HTTPSeeOther("/")


app = web.Application()
app.cleanup_ctx.append(bulb_connection)
app.router.add_get("/", index)
app.router.add_post("/power", set_power)
app.router.add_post("/warm", set_warm)
app.router.add_post("/brightness", set_brightness)
app.router.add_post("/color", set_color)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
