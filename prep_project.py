import socket
import asyncio

class Paginator:

    def welcome_page(self):
        return 200, 'welcome to our website'

    def home_page(self):
        return 200, 'this is a home page'


class Socket:

    def __init__(self):
        self.routes = {}
        self.status_texts = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
        
    async def handle_connection(self, reader, writer):
        data = await reader.read(1024)
        method, path, version, header, body = self.parse_request(data)
        status_code, respoce_body = self.get_responce(method, path, body)
        respoce = self.build_respoce(status_code, respoce_body)
        writer.write(respoce)
        await writer.drain()
        writer.close()

    async def serve(self, port=8080):
        server = await asyncio.start_server(self.handle_connection, "", port)
        async with server:
            await server.serve_forever()

    def parse_request(self, byte_data: bytes):
        data = byte_data.decode("utf-8")
        raw_data = data.split("\r\n")

        method, path, version = raw_data[0].split(" ")
        header = {}

        for i in raw_data[1:-2]:
            key, value = i.split(":", 1)
            header[key] = value.strip()

        body = raw_data[-1]

        return method, path, version, header, body

    def build_respoce(self, status_code: int, body: str) -> bytes:
        return f"HTTP/1.1 {status_code} {self.status_texts.get(status_code, 'Unknown')}\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()

    def add_route(self, method, path, handler):
        self.routes[(method, path)] = handler

    def get_responce(self, method, path, body=None):
        method_name = self.routes.get((method, path), None)
        if not method_name: return 404, "Not Found"
        return method_name()


s = Socket()
paginator = Paginator()
s.add_route('GET', '/', paginator.welcome_page)
s.add_route('GET', '/home', paginator.home_page)
asyncio.run(s.serve(8080))