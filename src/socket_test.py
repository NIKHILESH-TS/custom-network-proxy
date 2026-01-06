import socket

HOST = "127.0.0.1"
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"Listening on {HOST}:{PORT}")

conn, addr = server.accept()
print("Connected by", addr)

data = conn.recv(1024)
print("Received:", data.decode())

conn.sendall(b"Hello from server")
conn.close()
