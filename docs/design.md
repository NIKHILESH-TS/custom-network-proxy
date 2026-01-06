# Design Document — Custom Network Proxy Server

## 1. Architecture Overview

The proxy server acts as an intermediary between clients and destination servers.
It listens for incoming TCP connections, parses HTTP requests, applies filtering
rules, and forwards traffic accordingly.

### High-Level Architecture

Client → Proxy Server → Destination Server  
Client ← Proxy Server ← Destination Server

---

## 2. Concurrency Model

The proxy uses a **thread-per-connection** model:
- Each client connection is handled in a separate thread
- Threads are lightweight and daemonized
- This model is simple and sufficient for moderate concurrency

---

## 3. Request Processing Flow

1. Client connects to proxy
2. Proxy reads HTTP headers fully
3. Request is parsed (method, host, port, path)
4. Domain filtering rules are applied
5. If blocked → return HTTP 403
6. If allowed:
   - For HTTP → forward request and stream response
   - For HTTPS → establish CONNECT tunnel
7. Log request details
8. Close connection

---

## 4. HTTPS CONNECT Handling

When the proxy receives:
CONNECT host:port HTTP/1.1

vbnet
Copy code

Steps:
1. Establish TCP connection to host:port
2. Respond with:
HTTP/1.1 200 Connection Established

yaml
Copy code
3. Forward bytes bidirectionally using select()
4. Do not inspect TLS traffic

---

## 5. Logging Strategy

Each request is logged with:
- Timestamp
- Client IP and port
- Method
- Host and port
- Path
- Action (ALLOWED / BLOCKED)
- Bytes transferred

Logs are stored in `logs/proxy.log`.

---

## 6. Error Handling

- Malformed requests are dropped safely
- Missing Host header results in connection closure
- Socket errors are caught per-thread
- SIGINT terminates the server

---

## 7. Limitations

- No HTTP caching
- No POST body forwarding
- No authentication
- No chunked transfer decoding

These were intentionally excluded to keep the project focused on core networking concepts.
