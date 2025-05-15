from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
import models, schemas, database, auth
from datetime import timedelta
from typing import Optional
from fastapi import Query

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/users/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/users/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth.create_access_token(
        data={"sub": db_user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User)
async def update_user(user_update: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        current_user.hashed_password = pwd_context.hash(user_update.password)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/users/me")
async def delete_user(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return {"detail": "User deleted"}

@app.post("/todos", response_model=schemas.Todo)
async def create_todo(todo: schemas.TodoCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = models.Todo(**todo.model_dump(), user_id=current_user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos", response_model=list[schemas.Todo])
async def list_todos(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Todo).filter(models.Todo.user_id == current_user.id).all()

@app.get("/todos/search", response_model=list[schemas.Todo])
async def search_todos(q: Optional[str] = Query(None, min_length=1), current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.Todo).filter(models.Todo.user_id == current_user.id)
    if q:
        query = query.filter(models.Todo.title.ilike(f"%{q}%"))
    return query.all()

@app.get("/todos/{id}", response_model=schemas.Todo)
async def get_todo(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{id}", response_model=schemas.Todo)
async def update_todo(id: int, todo_update: schemas.TodoCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo_update.model_dump().items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{id}")
async def delete_todo(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == id, models.Todo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"detail": "Todo deleted"}