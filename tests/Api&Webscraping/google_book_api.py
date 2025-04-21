import requests


def get_book_by_isbn(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data)
        if "items" in data:
            book_info = data["items"][0]["volumeInfo"]
            title = book_info.get("title", "Unbekannter Titel")
            authors = ", ".join(book_info.get("authors", ["Unbekannter Autor"]))
            published_date = book_info.get("publishedDate", "Unbekanntes Datum")
            genre = ", ".join(book_info.get("categories"))
            language = book_info.get("language")
            thumbnail_link = book_info.get("imageLinks", {}).get("thumbnail", "Kein Bild vorhanden")
            page_count = book_info.get("pageCount", 0)
            if page_count == 0:
                page_count = "Nicht verfügbar"
            description = book_info.get("description", "Keine Beschreibung verfügbar.")

            short_description = description

            print(f"Titel: {title}")
            print(f"Autor(en): {authors}")
            print(f"Erscheinungsjahr: {published_date}")
            print(f"Seitenanzahl: {page_count}")
            print(f"Beschreibung: {short_description}")
            print(f"Genre: {genre}")
            print(f"Sprache: {language}")
            print(f"Link: {thumbnail_link}")
        else:
            print("Kein Buch gefunden.")
    else:
        print("Fehler beim Abruf der API.")


get_book_by_isbn("9780345391803")
