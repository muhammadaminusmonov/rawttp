import socket

def parse_request(byte_data: bytes):
    data = byte_data.decode("utf-8")
    raw_data = data.split("\r\n")

    method, path, version = raw_data[0].split(" ")
    header = {}

    for i in raw_data[1:-2]:
        key, value = i.split(":", 1)
        header[key] = value.strip()

    body = raw_data[-1]

    return method, path, version, header, body

s = socket.socket()
s.bind(("", 8080))
s.listen()

conn, add = s.accept()
data = conn.recv(1024)
method, path, version, headers, body = parse_request(data)
print(method, path, version)
print(headers)

conn.close()
s.close()

