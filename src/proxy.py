import socket
import threading
from datetime import datetime
import select

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8888
BUFFER_SIZE = 4096

BLOCKLIST_FILE = "config/blocked_domains.txt"
LOG_FILE = "logs/proxy.log"


def log_event(client_addr, method, host, port, path, action, size):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = (
        f"{timestamp} | "
        f"{client_addr[0]}:{client_addr[1]} | "
        f"{method} {host}:{port} {path} | "
        f"{action} | "
        f"{size} bytes\n"
    )
    with open(LOG_FILE, "a") as f:
        f.write(log_line)


def load_blocked_domains():
    blocked = set()
    try:
        with open(BLOCKLIST_FILE, "r") as f:
            for line in f:
                line = line.strip().lower()
                if line and not line.startswith("#"):
                    blocked.add(line)
    except FileNotFoundError:
        print("⚠️ Blocklist file not found")
    return blocked


BLOCKED_DOMAINS = load_blocked_domains()


def recv_until(sock, delimiter=b"\r\n\r\n"):
    data = b""
    while delimiter not in data:
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
    return data


def send_403(client_socket, host):
    response = (
        "HTTP/1.1 403 Forbidden\r\n"
        "Content-Type: text/plain\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"Access to {host} is blocked by proxy.\n"
    )
    client_socket.sendall(response.encode())
    return len(response)


def tunnel_data(client_socket, server_socket):
    sockets = [client_socket, server_socket]
    while True:
        readable, _, _ = select.select(sockets, [], [])
        for sock in readable:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                return
            if sock is client_socket:
                server_socket.sendall(data)
            else:
                client_socket.sendall(data)


def handle_client(client_socket, client_addr):
    bytes_sent = 0
    try:
        request_data = recv_until(client_socket)
        if not request_data:
            return

        header_text = request_data.decode(errors="ignore")
        lines = header_text.split("\r\n")

        request_line = lines[0]
        parts = request_line.split()
        if len(parts) != 3:
            return

        method, target, version = parts

        # ===================== CONNECT HANDLING =====================
        if method.upper() == "CONNECT":
            host, port = target.split(":")
            port = int(port)
            host = host.lower()

            if host in BLOCKED_DOMAINS:
                send_403(client_socket, host)
                log_event(client_addr, "CONNECT", host, port, "-", "BLOCKED", 0)
                return

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((host, port))

            client_socket.sendall(
                b"HTTP/1.1 200 Connection Established\r\n\r\n"
            )

            log_event(client_addr, "CONNECT", host, port, "-", "ALLOWED", 0)

            tunnel_data(client_socket, server_socket)
            server_socket.close()
            return

        # ===================== HTTP HANDLING =====================
        host = None
        port = 80

        for line in lines[1:]:
            if line.lower().startswith("host:"):
                host_value = line.split(":", 1)[1].strip()
                if ":" in host_value:
                    host, port = host_value.split(":")
                    port = int(port)
                else:
                    host = host_value
                break

        if not host:
            return

        host = host.lower()

        path = target
        if target.startswith("http://"):
            path = target.split("://", 1)[1]
            path = path[path.find("/"):]

        if host in BLOCKED_DOMAINS:
            bytes_sent = send_403(client_socket, host)
            log_event(client_addr, method, host, port, path, "BLOCKED", bytes_sent)
            return

        new_request_line = f"{method} {path} {version}\r\n"
        remaining_headers = "\r\n".join(lines[1:])
        new_request = (
            new_request_line + remaining_headers + "\r\n\r\n"
        ).encode()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, port))
        server_socket.sendall(new_request)

        while True:
            response = server_socket.recv(BUFFER_SIZE)
            if not response:
                break
            client_socket.sendall(response)
            bytes_sent += len(response)

        server_socket.close()
        log_event(client_addr, method, host, port, path, "ALLOWED", bytes_sent)

    except Exception as e:
        print("❌ Error:", e)

    finally:
        client_socket.close()


def start_proxy():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((LISTEN_HOST, LISTEN_PORT))
    proxy_socket.listen(50)

    print(f"🚀 Proxy listening on {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"🚫 Blocked domains: {BLOCKED_DOMAINS}")
    print(f"📝 Logging to {LOG_FILE}")

    while True:
        client_socket, addr = proxy_socket.accept()
        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr),
            daemon=True
        )
        thread.start()


if __name__ == "__main__":
    start_proxy()
