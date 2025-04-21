import re

def extract_email(sender_info):
    # Regex, um die E-Mail-Adresse aus dem Format "Name <email>" zu extrahieren
    match = re.search(r'<(.+?)>', sender_info)
    if match:
        return match.group(1)  # Gibt nur die E-Mail-Adresse zurück
    else:
        return sender_info  # Falls keine E-Mail-Adresse gefunden wird, gebe den gesamten Text zurück

# Beispiel:
sender = "El<guralnikelias390@gmail.com<>fhsks<f>"
email = extract_email(sender)

print(f"Nur die E-Mail-Adresse: {email}")
