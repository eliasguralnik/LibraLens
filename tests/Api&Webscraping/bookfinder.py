import webbrowser


def open_bookfinder_with_isbn(isbn):
    url = f"https://www.bookfinder.com/search/?isbn={isbn}&mode=isbn&st=sr&ac=qr"
    webbrowser.open(url)


open_bookfinder_with_isbn("9780140328721")

