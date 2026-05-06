# rawttp

A lightweight HTTP/1.1 server built from raw TCP sockets — no frameworks, no dependencies, just Python and `asyncio`.

Built as a deep-dive systems project to understand what every web framework is built on top of.

---

## Benchmark

Tested with JMeter — 200 concurrent threads, 60 seconds sustained load.

| | rawttp | nginx |
|---|---|---|
| **Throughput** | **64,049 req/sec** | 62,758 req/sec |
| Avg latency | 2ms | 2ms |
| Max latency | 49ms | 37ms |
| Error rate | 0.01% | 0.01% |

> rawttp outperforms nginx on throughput on the same machine. nginx has lower max latency under extreme load — expected for a C server with 20 years of optimization.

---

## Features

- Manual HTTP/1.1 request parsing — no `http.server`, no frameworks
- Keep-alive connections — reuses TCP connections across multiple requests
- Chunked transfer encoding — stream responses without knowing the full size upfront
- Async concurrent connections via `asyncio` — handles thousands of connections on a single thread
- Simple routing — register handlers with `add_route(method, path, handler)`

---

## Quick Start

```python
import asyncio
from server import Server

server = Server()

def home(request):
    return 200, "<h1>Hello, world!</h1>"

def about(request):
    return 200, "<h1>About</h1>"

server.add_route("GET", "/", home)
server.add_route("GET", "/about", about)

asyncio.run(server.serve(port=8080))
```

Visit `http://localhost:8080` — that's it.

---

## Chunked Responses

Return a `list` instead of a `str` from your handler to stream the response in chunks:

```python
def stream(request):
    chunks = ["Hello ", "from ", "chunked ", "encoding!"]
    return 200, chunks

server.add_route("GET", "/stream", stream)
```

rawttp automatically uses `Transfer-Encoding: chunked` when the body is a list. The browser reassembles the chunks transparently.

---

## API

### `Server()`

Creates a new server instance.

```python
server = Server()
```

---

### `server.add_route(method, path, handler)`

Registers a handler function for a given HTTP method and path.

```python
server.add_route("GET", "/hello", my_handler)
```

The handler receives a `Request` object and must return `(status_code, body)`:

```python
def my_handler(request):
    return 200, "Hello!"
```

| Parameter | Type | Description |
|---|---|---|
| `method` | `str` | HTTP method — `"GET"`, `"POST"`, etc. |
| `path` | `str` | URL path — `"/"`, `"/about"`, etc. |
| `handler` | `callable` | Function that takes a `Request` and returns `(int, str \| list)` |

---

### `server.serve(host, port)`

Starts the server. Blocks forever.

```python
asyncio.run(server.serve(port=8080))
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `host` | `str` | `""` | Host to bind to. `""` means all interfaces. |
| `port` | `int` | `8080` | Port to listen on. |

---

### `Request`

The object passed to every handler.

| Attribute | Type | Example |
|---|---|---|
| `request.method` | `str` | `"GET"` |
| `request.path` | `str` | `"/about"` |
| `request.version` | `str` | `"HTTP/1.1"` |
| `request.headers` | `dict` | `{"Host": "localhost:8080", ...}` |
| `request.body` | `str` | `""` |

---

## How It Works

```
Client                          rawttp
──────                          ──────
TCP connect         ──────────► asyncio.start_server()
                                    │
HTTP request bytes  ──────────►  reader.read(1024)
                                    │
                                 parse_request()
                                 → method, path, headers, body
                                    │
                                 route lookup
                                 → handler(request)
                                    │
                                 build_response() or
                                 build_chunked_response()
                                    │
HTTP response bytes ◄──────────  writer.write()
                                    │
                                 keep-alive? → loop
                                 Connection: close → close
```

Every connection runs as an `async` coroutine. While one connection is waiting for data, `asyncio` handles other connections. That's how a single Python thread serves 64k requests per second.

---

## Project Structure

```
rawttp/
├── server.py      # The library — Server, Request, parsers, response builders
├── example.py     # Example usage
└── README.md
```

---

## What I Learned

This project was built as part of a systems engineering roadmap — specifically to understand HTTP at the byte level before building distributed systems on top of it.

Building this taught me:
- What HTTP/1.1 actually is — a plain text protocol, nothing magical
- How TCP connections work at the socket level
- Why keep-alive matters — opening a new TCP connection per request is expensive
- What chunked encoding is and when to use it
- How `asyncio` achieves concurrency on a single thread via an event loop
- Why frameworks like FastAPI and Django are thin wrappers — the actual work is here

---

## License

MIT — see [LICENSE](LICENSE)