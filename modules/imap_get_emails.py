import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import re
from server.database import get_all_student_emails

EMAIL = "youremail@gmail.com"
PASSWORD = "yourpassword"
IMAP_SERVER = "imap.gmail.com"


def fill_allowed_senders():
    allowed_senders = get_all_student_emails()
    return allowed_senders


def main_process():
    sender_list = fill_allowed_senders()
    mess_list = fetch_filtered_emails(sender_list)
    return mess_list


date_since = (datetime.now() - timedelta(days=14)).strftime("%d-%b-%Y")


def clean_subject(subject):
    decoded, charset = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or "utf-8", errors="ignore")
    return decoded


def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    return part.get_payload(decode=True).decode(errors="ignore")
                except:
                    return None
    else:
        try:
            return msg.get_payload(decode=True).decode(errors="ignore")
        except:
            return None
    return None


def fetch_filtered_emails(allowed_senders):
    ALL_MESSAGES = []
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, f'(UNSEEN SINCE {date_since})')
    mail_ids = messages[0].split()

    if not mail_ids:
        print("Keine ungelesenen E-Mails in den letzten 14 Tagen gefunden.")
        return

    for mail_id in reversed(mail_ids):
        status, msg_data = mail.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                from_email = msg.get("From", "")

                if any(sender in from_email for sender in allowed_senders):
                    subject = clean_subject(msg.get("Subject", "Kein Betreff"))
                    body = get_body(msg)

                    if not body or not body.strip():
                        continue

                    print("Neue gefilterte Nachricht:")
                    print(mail_id)
                    print(f"Von: {from_email}")
                    print(f"Betreff: {subject}")
                    print("Inhalt:")
                    print(body.strip())
                    print("-" * 60)

                    match = re.search(r'<(.+?)>', from_email)
                    if match:
                        sender = match.group(1)
                    else:
                        sender = from_email

                    message = {
                        "id": mail_id,
                        "from": sender,
                        "subject": subject,
                        "content": body.strip()
                    }

                    ALL_MESSAGES.append(message)

    mail.logout()
    return ALL_MESSAGES



