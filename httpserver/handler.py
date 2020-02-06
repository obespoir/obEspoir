# coding=utf-8
"""
author = jamon
"""

from aiohttp import web

from httpserver.route import HttpHandler


@HttpHandler("/")
async def index(request):
    return web.Response(body="hello", content_type="text/html")
