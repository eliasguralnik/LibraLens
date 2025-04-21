import tkinter as tk

root = tk.Tk()
root.geometry("600x300")  # Fenstergröße
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

# Spalten konfigurieren, damit sie gleichmäßig Platz einnehmen
frame.columnconfigure(0, weight=1)  # Linke Spalte
frame.columnconfigure(1, weight=2)  # Mittlere Spalte (größer)
frame.columnconfigure(2, weight=1)  # Rechte Spalte

# Frames erstellen
frame1 = tk.Frame(frame, bg="red", width=100, height=200)
frame2 = tk.Frame(frame, bg="green", width=200, height=200)
frame3 = tk.Frame(frame, bg="blue", width=100, height=200)

# Frames platzieren
frame3.grid(row=0, column=0, sticky="nsew")  # Links
frame2.grid(row=0, column=1, sticky="nsew")  # Mitte
frame1.grid(row=0, column=2, sticky="nsew")  # Rechts

root.mainloop()
