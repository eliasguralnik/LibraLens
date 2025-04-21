import hashlib
import os

# Erzeuge ein zufälliges Salt
salt = os.urandom(16)  # 16 Byte Salt

# Passwort und Salt kombinieren und dann mit PBKDF2 hashen
password = b"meinSicheresPasswort"
hashed_password = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)

print(hashed_password.hex())