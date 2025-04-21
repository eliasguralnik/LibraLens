import socket
import ssl

HOST = 'localhost'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

print(f"Server läuft auf {HOST}:{PORT} (TLS aktiviert)")

while True:
    client_socket, addr = server_socket.accept()
    secure_socket = context.wrap_socket(client_socket, server_side=True)

    print(f"Sichere Verbindung von {addr}")

    secure_socket.send(b"Willkommen! Dies ist eine sichere Verbindung.")
    secure_socket.close()
