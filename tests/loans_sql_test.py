import sqlite3


# Verbindung zur SQLite-Datenbank herstellen
def connect_to_database():
    conn = sqlite3.connect('../database/library.db')  # Ersetze 'deine_datenbank.db' mit dem Pfad zu deiner Datenbank
    c = conn.cursor()
    return conn, c


def get_loan_data():
    try:
        # Verbindung und Cursor erstellen
        conn, c = connect_to_database()

        # SQL-Abfrage, um alle Ausleihdaten zu bekommen, dabei Namen und Titel statt IDs
        query = '''
        SELECT loans.loan_id, 
               students.name AS student_name, 
               books.title AS book_title, 
               loans.loan_date, 
               loans.return_date, 
               loans.status
        FROM loans
        JOIN students ON loans.student_id = students.id
        JOIN books ON loans.book_id = books.id
        '''

        # Ausführen der Abfrage
        c.execute(query)

        # Alle Ergebnisse abrufen
        data = c.fetchall()

        # Verbindung schließen
        conn.close()

        return data

    except Exception as e:
        print(f"Fehler: {e}")
        return None


# Beispiel: Daten abrufen und ausgeben
loan_data = get_loan_data()
if loan_data:
    for row in loan_data:
        print(row)
