from fastapi import FastAPI,Depends
from .database import Base, engine,SessionLocal
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from .models import Email
app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 👇 This runs when the app starts
    Base.metadata.create_all(bind=engine)
    yield
    # 👇 This runs when the app shuts down
    # (good place to close connections, cleanup, etc.)

app = FastAPI(lifespan=lifespan)
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
