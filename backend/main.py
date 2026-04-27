from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from auth import hash_password, create_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(username: str, password: str, role: str, db: Session = Depends(get_db)):
    user = models.User(
        username=username,
        password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    return {"msg": "User created"}

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=username).first()
    if not user:
        return {"error": "User not found"}
    token = create_token({"sub": user.username})
    return {"token": token}

@app.post("/courses")
def create_course(title: str, instructor_id: int, db: Session = Depends(get_db)):
    course = models.Course(title=title, instructor_id=instructor_id)
    db.add(course)
    db.commit()
    return {"msg": "Course created"}

@app.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()
