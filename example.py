"""
Example usage of rawttp.
"""

import asyncio
from server import Server


server = Server()


def home(request):
    return 200, "<h1>Welcome</h1><p>rawttp is running.</p>"


def about(request):
    return 200, "<h1>About</h1><p>Built from raw TCP sockets.</p>"


def stream(request):
    chunks = ["This ", "response ", "is ", "chunked!"]
    return 200, chunks


server.add_route("GET", "/", home)
server.add_route("GET", "/about", about)
server.add_route("GET", "/stream", stream)

asyncio.run(server.serve(port=8080))