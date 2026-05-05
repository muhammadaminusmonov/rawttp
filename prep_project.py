import socket

class Paginator:

    def welcome_page(self):
        return 200, 'welcome to our website'

    def home_page(self):
        return 200, 'this is a home page'


class Socket:

    def __init__(self):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", 8080))
        self.socket.listen()

        self.routes = {}
        paginator = Paginator()
        self.add_route('GET', '/', paginator.welcome_page)
        self.add_route('GET', '/home', paginator.home_page)


        self.conn, add = self.socket.accept()

        data = self.conn.recv(1024)
        method, path, version, headers, body = self.parse_request(data)
        status_code, responce_body = self.get_responce(method, path, body)
        self.send_response(status_code, responce_body)

        self.conn.close()
        self.socket.close()


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


    def send_response(self, status_code: int, body: str) -> bytes:
        self.conn.send(f"HTTP/1.1 {status_code} OK\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode())


    def add_route(self, method, path, handler):
        self.routes[(method, path)] = handler


    def get_responce(self, method, path, body=None):
        method_name = self.routes.get((method, path), None)
        if not method_name: return 404, "Not Found"
        return method_name()


s = Socket()

