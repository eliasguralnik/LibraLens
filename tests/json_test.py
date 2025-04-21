import json
import os
import time  # time ist notwendig, wenn du die Zeitstempel verwendest

session_id = 123
file_path = "sessions.json"
user_name = "elias"

# Die Sitzungsdaten
session = {
    "session_id": session_id,
    "client_socket": "client_socket",
    "created_at": time.time(),  # Zeitstempel für Erstellungszeit
    "last_activity": time.time(),  # Zeitstempel für letzte Aktivität
    "authenticated": False,
    "username": None
}
print(session)


# Funktion, um eine neue Sitzung hinzuzufügen oder die Datei zu erstellen
def create_sessions_json():
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        # Falls die Datei schon existiert, füge die neue Sitzung hinzu
        data.append(session)

    else:
        # Wenn die Datei nicht existiert, erzeuge eine Liste mit der ersten Sitzung
        data = [session]

    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("Daten wurden hinzugefügt oder bearbeitet!")


# Funktion, um eine Sitzung zu aktualisieren
def update_session_json(session_id_to_update):
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        # Suche nach der Sitzung mit der entsprechenden session_id
        for s in data:
            if s["session_id"] == session_id_to_update:
                s["authenticated"] = True  # Setze "authenticated" auf True
                s["username"] = user_name   # Setze den Benutzernamen

        # Speichere die geänderten Daten zurück in die Datei
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"Sitzung {session_id_to_update} wurde aktualisiert!")
    else:
        print("Die Datei existiert nicht!")


# Beispielaufruf der Funktionen
# create_sessions_json()  # Diese Funktion erstellt oder fügt eine Sitzung hinzu
update_session_json(223)  # Diese Funktion aktualisiert die Sitzung


