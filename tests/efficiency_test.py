import socket
import time
import struct

# Server starten
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 12345))
server.listen(1)

def handle_client(client):
    while True:
        data = client.recv(1024)
        if not data:
            break
    client.close()

# Server in neuem Thread starten
import threading
threading.Thread(target=lambda: handle_client(server.accept()[0]), daemon=True).start()

# Client-Verbindung aufbauen
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 12345))

# Test 1: Integer senden
start = time.perf_counter()
client.send(struct.pack("!I", 100))  # 100 als 4-Byte-Binärwert senden
end = time.perf_counter()
zeit_int = end - start

# Test 2: String senden
string_data = "close-client-connection"
s_start = time.perf_counter()
client.send(string_data.encode())  # String senden
s_end = time.perf_counter()
zeit_string = s_end - s_start
diff = zeit_int - zeit_string
print(diff)
print("int", zeit_int)
print("string", zeit_string)
client.close()
server.close()
