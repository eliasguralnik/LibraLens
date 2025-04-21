from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def find_book_by_isbn_with_selenium(isbn):
    # Starte den WebDriver (z. B. Chrome)
    driver = webdriver.Chrome()

    # Die URL von BookFinder für die Suche nach einer ISBN
    url = f"https://www.bookfinder.com/search/?author=&title=&lang=en&submitBtn=Search&new_used=*&destination=il&currency=ILS&binding=*&isbn={isbn}&keywords=&minprice=&maxprice=&publisher=&min_year=&max_year=&mode=advanced&st=sr&ac=qr"
    driver.get(url)

    # Warte einige Sekunden, bis die Seite geladen ist
    time.sleep(5)  # Wartezeit anpassen, je nachdem, wie schnell die Seite lädt

    # Versuche, den Link zum Buch zu finden
    try:
        # Suche nach dem ersten Link, der die Klasse 'clickout-logger' hat
        link_element = driver.find_element(By.CLASS_NAME, 'clickout-logger')
        book_url = link_element.get_attribute('href')
        print(f"Buch gefunden: {book_url}")
    except Exception as e:
        print(f"Fehler beim Extrahieren des Links: {e}")

    # Schließe den Browser
    driver.quit()

# Testen mit einer ISBN
isbn = "9783161484100"
find_book_by_isbn_with_selenium(isbn)
