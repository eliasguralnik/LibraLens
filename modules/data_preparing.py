import sqlite3
import json
import os

prepared_data_library = []


def connect_to_database():
    try:
        conn = sqlite3.connect('../database/library.db')
        c = conn.cursor()
        return conn, c
    except Exception as e:
        print("Fehler beim Verbinden mit der Datenbank:", e)
        return None, None


def get_book_data():
    conn, c = connect_to_database()
    if not conn or not c:
        return []

    try:
        c.execute('''SELECT * FROM books''')
        return c.fetchall()
    except Exception as e:
        print("Fehler beim Abrufen der Bücher:", e)
        return []
    finally:
        conn.close()


def prepare_library_data():
    data = get_book_data()

    counter_list = []
    for book in data:
        isbn = book[1].strip()
        title = book[2]
        descr = book[4]
        genre = book[7]
        counter = 0

        if os.path.exists("../docs/returned-loans.json"):
            try:
                with open("../docs/returned-loans.json", "r") as json_file:
                    returned_loans = json.load(json_file)

                if isinstance(returned_loans, list):
                    for s in returned_loans:
                        if s.get("book_isbn") == isbn:
                            counter += 1
            except (json.JSONDecodeError, IOError) as e:
                print("Fehler beim Laden der JSON-Datei:", e)

        counter_list.append(counter)
        prepared_data_library.append((title, genre, descr, counter))

    total_loans = sum(counter_list)

    if total_loans > 0:
        for i in range(len(prepared_data_library)):
            title, genre, descr, loans = prepared_data_library[i]
            weight_number = loans / total_loans
            prepared_data_library[i] = (title, genre, descr, weight_number)

    return prepared_data_library


def prepare_new_data():
    prepared_data_new_list = []
    with open("../docs/books_data.json", "r") as json_file:
        data = json.load(json_file)
    for book in data:
        new_book = (book["title"], book["genre"], book["description"])
        prepared_data_new_list.append(new_book)

    return prepared_data_new_list


if __name__ == '__main__':
    prepare_library_data()
    prepare_new_data()
