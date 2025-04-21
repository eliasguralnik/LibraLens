import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

# Importiere für macOS/Linux den CUPS-API
if sys.platform == "darwin" or sys.platform.startswith('linux'):
    import cups

# Funktion zum Drucken mit macOS/Linux (CUPS)
def print_file_mac_linux(file_path):
    try:
        conn = cups.Connection()  # Erstelle eine Verbindung zu CUPS
        printers = conn.getPrinters()  # Hole alle verfügbaren Drucker

        if printers:
            # Wähle den ersten verfügbaren Drucker (oder stelle sicher, dass der Benutzer ihn auswählt)
            printer_name = list(printers.keys())[0]  # Du kannst auch eine Benutzerwahl implementieren
            print(f"Verfügbare Drucker: {printers}")

            # Druckauftrag senden
            conn.printFile(printer_name, file_path, "Druckauftrag", {})
            print(f"Die Datei {file_path} wird an den Drucker {printer_name} gesendet.")
        else:
            print("Kein Drucker gefunden.")
            messagebox.showerror("Fehler", "Kein Drucker verfügbar!")
    except Exception as e:
        print(f"Fehler beim Drucken: {e}")
        messagebox.showerror("Fehler", f"Fehler beim Drucken: {e}")

# Funktion zur Auswahl des Druckers und zum Drucken
def select_printer_and_print():
    file_path = filedialog.askopenfilename(title="Wählen Sie eine Datei zum Drucken", filetypes=[("Alle Dateien", "*.*")])

    if file_path:
        if sys.platform == "darwin" or sys.platform.startswith('linux'):
            print_file_mac_linux(file_path)
    else:
        messagebox.showerror("Fehler", "Keine Datei ausgewählt!")

# Erstelle eine einfache GUI mit tkinter
def create_gui():
    root = tk.Tk()
    root.title("Drucker Auswahl und Einstellungen")

    # Druck-Button
    print_button = tk.Button(root, text="Drucker auswählen und drucken", command=select_printer_and_print)
    print_button.pack(pady=20)

    # Schließe die GUI
    root.mainloop()

if __name__ == "__main__":
    create_gui()
