"""
rawttp — A lightweight HTTP/1.1 server built from raw TCP sockets.

Supports:
- Manual HTTP/1.1 request parsing
- Keep-alive connections
- Chunked transfer encoding
- Async concurrent connections via asyncio
"""

import asyncio


STATUS_TEXTS = {
    200: "OK",
    201: "Created",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
}


class Request:
    """Represents a parsed HTTP request."""

    def __init__(self, method: str, path: str, version: str, headers: dict, body: str):
        self.method = method
        self.path = path
        self.version = version
        self.headers = headers
        self.body = body


class Server:
    """
    A lightweight async HTTP/1.1 server built from raw TCP sockets.

    Usage:
        server = Server()
        server.add_route("GET", "/", handler)
        asyncio.run(server.serve())
    """

    def __init__(self):
        self.routes: dict = {}

    def add_route(self, method: str, path: str, handler) -> None:
        """Register a route handler for a given HTTP method and path.

        The handler must return a tuple of (status_code, body).
        Body can be a str (normal response) or list[str] (chunked response).

        Example:
            def home(request):
                return 200, "Hello, world!"

            server.add_route("GET", "/", home)
        """
        self.routes[(method.upper(), path)] = handler

    async def serve(self, host: str = "", port: int = 8080) -> None:
        """Start the server and listen for connections."""
        server = await asyncio.start_server(self._handle_connection, host, port)
        addr = server.sockets[0].getsockname()
        print(f"rawttp serving on http://{addr[0] or 'localhost'}:{addr[1]}")
        async with server:
            await server.serve_forever()

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle a single TCP connection, supporting keep-alive."""
        while True:
            data = await reader.read(1024)
            if data == b"":
                break

            request = self._parse_request(data)
            status_code, body = self._dispatch(request)

            if isinstance(body, list):
                response = self._build_chunked_response(status_code, body)
            else:
                response = self._build_response(status_code, body)

            writer.write(response)
            await writer.drain()

            if request.headers.get("Connection") == "close":
                break

        writer.close()

    def _parse_request(self, raw: bytes) -> Request:
        """Parse raw bytes into a Request object."""
        text = raw.decode("utf-8")
        lines = text.split("\r\n")

        method, path, version = lines[0].split(" ")

        headers = {}
        for line in lines[1:-2]:
            if line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        body = lines[-1]
        return Request(method, path, version, headers, body)

    def _dispatch(self, request: Request) -> tuple:
        """Look up and call the handler for the given request."""
        handler = self.routes.get((request.method, request.path))
        if handler is None:
            return 404, "Not Found"
        return handler(request)

    def _build_response(self, status_code: int, body: str) -> bytes:
        """Build a standard HTTP/1.1 response with Content-Length."""
        status_text = STATUS_TEXTS.get(status_code, "Unknown")
        return (
            f"HTTP/1.1 {status_code} {status_text}\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"\r\n"
            f"{body}"
        ).encode()

    def _build_chunked_response(self, status_code: int, chunks: list) -> bytes:
        """Build a chunked HTTP/1.1 response (Transfer-Encoding: chunked)."""
        status_text = STATUS_TEXTS.get(status_code, "Unknown")
        body = ""
        for chunk in chunks:
            body += f"{format(len(chunk), 'x')}\r\n{chunk}\r\n"
        body += "0\r\n\r\n"
        return (
            f"HTTP/1.1 {status_code} {status_text}\r\n"
            f"Transfer-Encoding: chunked\r\n"
            f"\r\n"
            f"{body}"
        ).encode()