from datetime import datetime
from fastapi import FastAPI, Depends
from .database import Base, engine, SessionLocal
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from .models import Email
from .email_service import fetch_emails
from email.utils import parsedate_to_datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 👇 This runs when the app starts
    Base.metadata.create_all(bind=engine)
    yield
    # 👇 This runs when the app shuts down
    # (good place to close connections, cleanup, etc.)


app = FastAPI(lifespan=lifespan)


# Dependency to get Db session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/check-db")
def check_db(db: Session = Depends(get_db)):
    # Just try to query the emails table
    return {"emails_count": db.query(Email).count()}


@app.get("/")
def root():
    return {"message": "Hello, FastAPI is working!"}


from email.utils import parsedate_to_datetime


@app.get("/emails/fetch")
def fetch_and_store_emails(db: Session = Depends(get_db)):
    emails = fetch_emails(limit=10)  # fetch 10 latest support emails
    stored = 0

    print(f"\n=== Raw Fetched Emails ({len(emails)}) ===")
    for idx, e in enumerate(emails, 1):
        print(f"[{idx}] Subject: {e['subject']}, Sender: {e['sender']}")

        # Check if email already exists
        existing = (
            db.query(Email)
            .filter(Email.subject == e["subject"], Email.sender == e["sender"])
            .first()
        )

        if existing:
            print(f"--> Skipped (duplicate found in DB) :: {existing.subject}")
            continue

        # Parse date safely
        date_str = e.get("date_received")
        try:
            parsed_date_received = parsedate_to_datetime(date_str) if date_str else None
        except Exception as ex:
            print(f"!! Failed to parse date '{date_str}', using now(). Error: {ex}")
            parsed_date_received = None

        if not parsed_date_received:
            parsed_date_received = datetime.now()

        # Insert into DB
        email_entry = Email(
            sender=e["sender"],
            subject=e["subject"],
            body=e["body"],
            date_received=parsed_date_received,
        )
        db.add(email_entry)
        stored += 1
        print(f"--> Inserted into DB: {e['subject']}")

    db.commit()
    print(f"=== Summary: {stored} new stored, {len(emails) - stored} skipped ===\n")
    return {"fetched": len(emails), "stored_new": stored}


@app.get("/emails/list")
def list_emails(db: Session = Depends(get_db)):
    emails = db.query(Email).all()
    return [
        {
            "id": e.id,
            "sender": e.sender,
            "subject": e.subject,
            "date_received": e.date_received,
            "status": e.status,
        }
        for e in emails
    ]
