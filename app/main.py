from datetime import datetime
from fastapi import FastAPI,Depends
from .database import Base, engine,SessionLocal
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from .models import Email
from .email_service import fetch_emails

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 👇 This runs when the app starts
    Base.metadata.create_all(bind=engine)
    yield
    # 👇 This runs when the app shuts down
    # (good place to close connections, cleanup, etc.)

app = FastAPI(lifespan=lifespan)

#Dependency to get Db session per request
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

@app.get("/emails/fetch")
def fetch_and_store_emails(db: Session = Depends(get_db)):
    emails = fetch_emails(limit=10)  # fetch 10 latest support emails
    stored = 0

    for e in emails:
        # Avoid duplicates (by subject + sender check)
        existing = db.query(Email).filter(
            Email.subject == e["subject"], 
            Email.sender == e["sender"]
        ).first()

        if not existing:
            email_entry = Email(
                sender=e["sender"],
                subject=e["subject"],
                body=e["body"],
                date_received=datetime.now()  # could parse e["date_received"] instead
            )
            db.add(email_entry)
            stored += 1

    db.commit()
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
            "status": e.status
        }
        for e in emails
    ]