from app.email_service import fetch_emails

emails = fetch_emails(limit=5)
for e in emails:
    print(f"From: {e['sender']}")
    print(f"Subject: {e['subject']}")
    print(f"Date: {e['date_received']}")
    print(f"Body: {e['body'][:100]}...\n")
