import requests
import json
import random
import time

API_URL = "https://www.googleapis.com/books/v1/volumes"

SEARCH_TERMS = [
    "bestseller", "classic books", "famous novels", "award-winning books",
    "popular fiction", "top 100 books", "must read books", "greatest novels",
    "famous authors", "influential books", "fantasy bestsellers", "top science fiction",
    "historical fiction", "mystery bestsellers", "top romance books", "horror classics",
    "modern literature", "Shakespeare books", "detective novels", "young adult fiction",
    "dystopian novels", "post-apocalyptic books", "non-fiction bestsellers",
    "self-improvement books", "psychology books", "business books", "startup books",
    "biographies of famous people", "political thrillers", "military history books",
    "philosophy classics", "spiritual books", "mindfulness books", "medieval literature",
    "Renaissance books", "Greek mythology books", "Roman Empire books", "World War II novels",
    "famous poetry books", "science books", "technology books", "space exploration books",
    "quantum physics books", "AI and machine learning books", "coding books", "startup books",
    "marketing books", "economics books", "investment books", "stock market books",
    "crime fiction", "cyberpunk novels", "steampunk novels", "time travel books",
    "epic fantasy", "vampire novels", "werewolf books", "fairy tale retellings",
    "Arthurian legends", "King Arthur books", "Sherlock Holmes books", "Agatha Christie books",
    "J.R.R. Tolkien books", "J.K. Rowling books", "Stephen King novels", "H.P. Lovecraft books",
    "Isaac Asimov books", "George Orwell books", "Aldous Huxley books", "Ernest Hemingway books",
    "F. Scott Fitzgerald books", "Jane Austen books", "Charles Dickens books", "Mark Twain books",
    "Leo Tolstoy books", "Fyodor Dostoevsky books", "Franz Kafka books", "Gabriel Garcia Marquez books",
    "Haruki Murakami books", "Kurt Vonnegut books", "Margaret Atwood books", "Neil Gaiman books",
    "Terry Pratchett books", "Douglas Adams books", "Ray Bradbury books", "Philip K. Dick books",
    "Brandon Sanderson books", "Robert Jordan books", "Ursula K. Le Guin books", "Octavia Butler books"
]


def process_book_scraper():
    books_data = []
    MAX_BOOKS = 100
    BOOKS_PER_QUERY = 40
    SEEN_ISBNS = set()
    try:
        while len(books_data) < MAX_BOOKS:
            search_term = random.choice(SEARCH_TERMS)
            params = {
                "q": search_term,
                "maxResults": BOOKS_PER_QUERY,
                "langRestrict": "en",
                "printType": "books"
            }

            response = requests.get(API_URL, params=params)

            if response.status_code == 200:
                books = response.json().get("items", [])

                for book in books:
                    volume_info = book.get("volumeInfo", {})
                    title = volume_info.get("title", "Unknown Title")
                    genre = volume_info.get("categories", ["Unknown Genre"])[0]
                    description = volume_info.get("description", "No Description Available")
                    isbn = next(
                        (id["identifier"] for id in volume_info.get("industryIdentifiers", []) if id["type"] == "ISBN_13"),
                        None)

                    if isbn and isbn not in SEEN_ISBNS:
                        SEEN_ISBNS.add(isbn)
                        books_data.append({
                            "isbn": isbn,
                            "title": title,
                            "genre": genre,
                            "description": description
                        })

                    if len(books_data) >= MAX_BOOKS:
                        break

            print(f"{len(books_data)} books collected so far...")

            time.sleep(1)

        with open("../docs/books_data.json", "w", encoding="utf-8") as f:
            json.dump(books_data, f, ensure_ascii=False, indent=4)

        print(f"Finished! {len(books_data)} books saved.")
        return True

    except Exception as e:
        print(e)
        return False


def scrape_thumbnail_link(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            book_info = data["items"][0]["volumeInfo"]
            thumbnail_link = book_info.get("imageLinks", {}).get("thumbnail", "Kein Bild vorhanden")
            return thumbnail_link
        else:
            print("Kein Buch gefunden.")
            return None
    else:
        print("Fehler beim Abruf der API.")
        return None
