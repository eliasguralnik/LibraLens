import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from dateutil.relativedelta import relativedelta
import barcode
from barcode.writer import ImageWriter
import io


# Funktion, um das Bild zu erstellen und zu speichern
def create_card(student_name, class_, teacher, student_id):
    # Ablaufdatum berechnen
    card_expiration_date = datetime.today() + relativedelta(years=1)
    width, height = 450, 300

    # Neues Bild erstellen
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Schriftart laden (hier Arial, stelle sicher, dass diese Schriftart vorhanden ist)
    try:
        font = ImageFont.truetype("arial.ttf", 15)  # Schriftart mit Größe 15
    except IOError:
        font = ImageFont.load_default()  # Falls Arial nicht vorhanden ist, Standard-Schriftart verwenden

    # Text auf das Bild zeichnen
    draw.text((25, 20), "Student Card", fill="black", font=font)
    draw.text((25, 100), f"Vorname: {student_name}", fill="black", font=font)
    draw.text((25, 130), f"Class: {class_}", fill="black", font=font)
    draw.text((25, 160), f"Teacher: {teacher}", fill="black", font=font)
    draw.text((260, 270), f"Expiring date: {card_expiration_date.strftime('%Y-%m-%d')}", fill="black", font=font)
    draw.text((260, 240), f"Issue date: {datetime.today().strftime('%Y-%m-%d')}", fill="black", font=font)

    # Logo-Bild einfügen
    logo_image = Image.open("Logo_School.png").convert("RGBA")
    logo_image = logo_image.resize((logo_image.width // 4, logo_image.height // 4))
    image.paste(logo_image, (200, 10), logo_image)

    # Barcode generieren
    ean = barcode.get_barcode_class('ean13')
    ean_barcode = ean(str(student_id), writer=ImageWriter())

    # Barcode im Speicher erzeugen
    with io.BytesIO() as barcode_buffer:
        ean_barcode.write(barcode_buffer)
        barcode_buffer.seek(0)

        barcode_image = Image.open(barcode_buffer).convert("RGBA")

        # Barcode-Größe anpassen
        barcode_image = barcode_image.resize((160, 80))

        # Barcode-Bild auf das Kartenbild einfügen
        image.paste(barcode_image, (5, 220), barcode_image)

    # Dateidialog öffnen, um den Speicherort auszuwählen
    save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])

    # Wenn der Benutzer einen Pfad gewählt hat, speichern wir das Bild
    if save_path:
        image.save(save_path)
        print(f"Bild gespeichert unter {save_path}")
    else:
        print("Kein Speicherort gewählt.")


# Tkinter Fenster initialisieren
root = tk.Tk()
root.withdraw()  # Das Hauptfenster nicht anzeigen

# Beispielaufruf
create_card("Max Mustermann", "10A", "Herr Schmidt", 123456789012)
