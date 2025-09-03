import imaplib, email
from email.header import decode_header
from datetime import datetime

SUPPORT_KEYWORDS = ["support", "query", "request", "help"]

def fetch_emails(username, password, imap_url="imap.gmail.com", mailbox="inbox", limit=20):
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(username, password)
    mail.select(mailbox)

    _, messages = mail.search(None, "ALL")
    messages = messages[0].split()
    latest_messages = messages[-limit:]

    emails = []

    for msg_num in latest_messages:
        _, msg_data = mail.fetch(msg_num, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")

        from_ = msg.get("From")
        date_ = msg.get("Date")
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        # Filtering by keywords in subject
        if any(word.lower() in subject.lower() for word in SUPPORT_KEYWORDS):
            emails.append({
                "sender": from_,
                "subject": subject,
                "body": body,
                "date_received": date_
            })

    mail.logout()
    return emails
