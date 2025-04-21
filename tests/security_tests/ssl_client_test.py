import socket
import ssl

context = ssl.create_default_context()
context.load_verify_locations("server.crt")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_socket = context.wrap_socket(client_socket, server_hostname="localhost")

secure_socket.connect(("localhost", 12345))

data = secure_socket.recv(1024)
print(f"Server sagt: {data.decode()}")

secure_socket.close()
