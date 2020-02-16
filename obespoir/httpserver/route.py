# coding=utf-8
"""
author = jamon
"""


class HttpHandler(object):

    def __init__(self, url):
        self.url = url

    def __call__(self, handler):
        from obespoir.server.server import Server
        Server().register_web_route(self.url, handler)