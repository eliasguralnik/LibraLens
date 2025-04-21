import webbrowser
import urllib.parse

empfaenger = "ziel@example.com"
betreff = "Anfrage bezüglich Ihres Produkts"

# E-Mail-Hauptteil (Schablone)
body_text = """\
Sehr geehrte Damen und Herren,

ich interessiere mich für Ihr Produkt und hätte dazu ein paar Fragen:

1. ...
2. ...
3. ...

Mit freundlichen Grüßen
Elias
"""

# Alles codieren
subject_encoded = urllib.parse.quote(betreff)
body_encoded = urllib.parse.quote(body_text)

# Mailto-Link
mailto_link = f"mailto:{empfaenger}?subject={subject_encoded}&body={body_encoded}"

# Öffnen
webbrowser.open(mailto_link)
