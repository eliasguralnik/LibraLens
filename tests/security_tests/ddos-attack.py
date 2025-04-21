import time
from collections import defaultdict

request_times = defaultdict(list)

MAX_REQUESTS_PER_SECOND = 5
active_connections = defaultdict(int)


def handle_connection(client_ip):
    active_connections[client_ip] += 1  # Verbindung zählen

    if active_connections[client_ip] > 10:  # Mehr als 10 Verbindungen?
        print(f"🚨 Blockiert: {client_ip} (zu viele Anfragen!)")
        return False  # Verbindung verweigern

    print(f"✅ Verbindung erlaubt: {client_ip} (Anzahl: {active_connections[client_ip]})")
    return True


# # Simulation von Verbindungen
# for _ in range(12):
#     handle_connection("192.168.1.1")


def is_rate_limited(ip):
    current_time = time.time()
    # Entfernt Anfragen, die älter als 1 Sekunde sind
    request_times[ip] = [t for t in request_times[ip] if current_time - t < 1]

    if len(request_times[ip]) >= MAX_REQUESTS_PER_SECOND:
        return True  # IP ist rate-limited
    else:
        request_times[ip].append(current_time)
        return False  # IP ist nicht rate-limited


def handle_client_request(ip):
    if is_rate_limited(ip):
        print(f"Rate limit exceeded for IP {ip}. Blocking request.")
        return "429 Too Many Requests"  # HTTP 429 Statuscode für zu viele Anfragen
    else:
        print(f"Request from IP {ip} is allowed.")
        return "200 OK"  # Erfolgreiche Anfrage


for _ in range(12):
    handle_client_request("192.168.1.1")

