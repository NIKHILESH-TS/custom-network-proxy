# Custom Network Proxy Server

## Overview
This project implements a **forward HTTP/HTTPS proxy server** using Python sockets.
The proxy accepts client requests, forwards them to destination servers, and relays
responses back to clients. It supports **concurrent clients**, **domain filtering**,
**logging**, and **HTTPS tunneling via CONNECT**.

The project demonstrates core systems and networking concepts such as:
- TCP socket programming
- Multithreading
- HTTP request parsing
- Traffic filtering
- Logging and testing

---

## Features
- Forward proxy for HTTP traffic
- HTTPS support using CONNECT tunneling
- Thread-per-connection concurrency model
- Configurable domain/IP blocking
- Detailed request logging
- Streaming request/response forwarding
- Graceful handling of malformed requests

---

## Project Structure
 
proxy-project/
 ├── src/ # Proxy server source code
 ├── config/ # Configuration files (blocked domains)
 ├── logs/ # Proxy logs
 ├── tests/ # Test commands and examples
 ├── docs/ # Design documentation
 └── README.md


---

## Requirements
- Python 3.8+
- Linux environment
- curl (for testing)

---

## How to Run

1. Activate virtual environment (if used):
```bash
    source venv/bin/activate
2. Start the proxy server:

    python3 src/proxy.py


The proxy listens on:

    127.0.0.1:8888

Configuration :

Blocked Domains:
Edit the file:

    config/blocked_domains.txt


Example:

    example.com
    badsite.org


Changes take effect after restarting the proxy.

Testing
HTTP Request
    curl -x 127.0.0.1:8888 http://example.com

HEAD Request
    curl -x 127.0.0.1:8888 -I http://example.com

HTTPS Request
    curl -x 127.0.0.1:8888 https://iana.org

Concurrent Requests

Run the same curl command from multiple terminals simultaneously.

Logging

Logs are written to:

    logs/proxy.log


Each log entry includes:

	Timestamp
	Client IP and port
	HTTP method
	Destination host and port
	Request path
	Action (ALLOWED / BLOCKED)
	Bytes transferred

Limitations

POST request bodies are not fully handled

Chunked transfer encoding is not parsed

No HTTP caching implemented

No authentication support

Graceful shutdown via SIGINT only

Security Notes

TLS traffic is not decrypted or inspected

HTTPS is tunneled transparently using CONNECT

No sensitive data is logged

Author

Nikhilesh
(Custom Proxy Server – Systems & Networking Project)


Save and exit.
