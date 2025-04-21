from datetime import datetime
from tkinter import filedialog
from dateutil.relativedelta import relativedelta
import barcode
from barcode.writer import ImageWriter
import isbnlib
from PIL import Image, ImageDraw, ImageFont
import io
import os


def create_card(student_name, class_, teacher, student_id):
    student_id = str(student_id).zfill(8)

    card_expiration_date = datetime.today() + relativedelta(years=1)
    width, height = 450, 300

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    draw.text((25, 30), "Student Card", fill="black", font_size=22)
    draw.text((25, 120), f"Name: {student_name}", fill="black", font=font)
    draw.text((25, 150), f"Class: {class_}", fill="black", font=font)
    draw.text((25, 180), f"Teacher: {teacher}", fill="black", font=font)
    draw.text((260, 120), f"Expiring date: {card_expiration_date.strftime('%Y-%m-%d')}", fill="black", font=font)
    draw.text((260, 150), f"Issue date: {datetime.today().strftime('%Y-%m-%d')}", fill="black", font=font)

    try:
        logo_image = Image.open("../assets/Logo_School.png").convert("RGBA")
        logo_image = logo_image.resize((logo_image.width // 4, logo_image.height // 4))
        image.paste(logo_image, (200, 20), logo_image)
    except FileNotFoundError:
        print("Logo konnte nicht gefunden werden.")

    ean = barcode.get_barcode_class('ean8')
    ean_barcode = ean(student_id, writer=ImageWriter())

    with io.BytesIO() as barcode_buffer:
        ean_barcode.write(barcode_buffer)
        barcode_buffer.seek(0)

        barcode_image = Image.open(barcode_buffer).convert("RGBA")
        barcode_image = barcode_image.resize((160, 80))

        image.paste(barcode_image, (240, 210), barcode_image)

    return image


def process_single_card_creation(student_name, class_, teacher, student_id):
    student_card = create_card(student_name, class_, teacher, student_id)
    save_folder = filedialog.askdirectory(title="Wählen Sie einen Ordner zum Speichern der Karten")
    if save_folder:
        save_path = os.path.join(save_folder, f"student_card_{student_id}.png")
        student_card.save(save_path)
        return save_path
    else:
        print("Kein Ordner gewählt.")
        return None


def process_all_card_creation(student_name, class_, teacher, student_id):
    student_card = create_card(student_name, class_, teacher, student_id)
    return student_card


def create_barcode(isbn):
    if len(isbn) == 10:
        isbn = isbnlib.to_isbn13(isbn)

    ean = barcode.get_barcode_class('ean13')
    ean_barcode = ean(isbn, writer=ImageWriter())

    with io.BytesIO() as barcode_buffer:
        ean_barcode.write(barcode_buffer)
        barcode_buffer.seek(0)

        barcode_image = Image.open(barcode_buffer).convert("RGBA")
        barcode_image = barcode_image.resize((160, 80))
        return barcode_image
