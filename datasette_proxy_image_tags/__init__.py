import httpx
import functools
import logging
from datasette import hookimpl
from urllib.parse import quote_plus
from markupsafe import Markup, escape

logger = logging.getLogger(__name__)
client = httpx.AsyncClient()


async def proxy(request, send):
    async with client.stream("GET", request.args["url"]) as response:
        await send(
            {
                "type": "http.response.start",
                "status": response.status_code,
                "headers": [
                    [key.encode("utf-8"), value.encode("utf-8")]
                    for key, value in response.headers.items()
                    if key.lower() in ("content-length", "content-encoding")
                ],
            }
        )
        async for chunk in response.aiter_raw():
            await send(
                {
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True,
                }
            )
        await send({"type": "http.response.body", "body": b""})


@hookimpl
def register_routes():
    return [
        (r"^/-/proxy$", proxy),
    ]


@hookimpl
def render_cell(datasette, database, table, column, value):
    config = datasette.plugin_config("datasette-proxy-image-tags", database=database, table=table)
    if not config:
        return
    columns = config.get("columns", [])
    if column not in columns:
        return
    if not isinstance(value, str):
        return
    value = value.strip()
    if not value or " " in value:
        return
    if not (value.startswith("http://") or value.startswith("https://")):
        return
    return Markup('<img src="{}" width="200" loading="lazy">'.format(escape(f"/-/proxy?url={quote_plus(value)}")))


@hookimpl
def asgi_wrapper():
    def wrapped(app):
        @functools.wraps(app)
        async def serve(scope, request, send):
            async def wrapped_send(event):
                if event["type"] == "lifespan.shutdown.complete":
                    logging.info("Closing httpx proxy...")
                    await client.aclose()
                await send(event)
            await app(scope, request, wrapped_send)
        return serve
    return wrapped