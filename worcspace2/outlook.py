from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Конфигурация JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Псевдо-база данных
users_db = []
folders_db = []
messages_db = []

# Модель пользователя
class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    first_name: str
    last_name: str
    email: str

# Модель почтовой папки
class Folder(BaseModel):
    id: int
    user_id: int
    name: str

# Модель сообщения
class Message(BaseModel):
    id: int
    folder_id: int
    subject: str
    content: str
    created_at: datetime

# Создание токена доступа
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Получение текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = next((u for u in users_db if u.username == username), None)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

# Мастер-пользователь
master_user = User(
    id=1,
    username="admin",
    hashed_password=pwd_context.hash("$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"),
    first_name="Admin",
    last_name="User",
    email="admin@example.com"
)
users_db.append(master_user.dict())

# Маршрут для получения токена
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in users_db if u.username == form_data.username), None)
    if user and pwd_context.verify(form_data.password, user["hashed_password"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Создание нового пользователя
@app.post("/users", response_model=User )
def create_user(user: User):
    if any(u["username"] == user.username for u in users_db):
        raise HTTPException(status_code=400, detail="User  already exists")
    user.id = len(users_db) + 1  # Присваиваем новый ID
    user.hashed_password = pwd_context.hash(user.hashed_password)  # Хешируем пароль
    users_db.append(user.dict())
    return user

# Поиск пользователя по логину
@app.get("/users/{username}", response_model=User )
def get_user_by_username(username: str):
    user = next((u for u in users_db if u["username"] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User  not found")
    return user

# Поиск пользователя по маске имени и фамилии
@app.get("/users", response_model=List[User ])
def search_users(first_name: str, last_name: str):
    matching_users = [
        User(**user) for user in users_db
        if first_name.lower() in user["first_name"].lower() and last_name.lower() in user["last_name"].lower()
    ]
    return matching_users

# Создание новой почтовой папки
@app.post("/folders", response_model=Folder)
def create_folder(folder: Folder, current_user: User = Depends(get_current_user)):
    folder.id = len(folders_db) + 1  # Присваиваем новый ID
    folder.user_id = current_user.id
    folders_db.append(folder.dict())
    return folder

# Получение перечня всех папок
@app.get("/folders", response_model=List[Folder])
def get_folders(current_user: User = Depends(get_current_user)):
    user_folders = [folder for folder in folders_db if folder["user_id"] == current_user.id]
    return user_folders

# Создание нового сообщения в папке
@app.post("/messages", response_model=Message)
def create_message(message: Message, current_user: User = Depends(get_current_user)):
    if not any(folder["id"] == message.folder_id and folder["user_id"] == current_user.id for folder in folders_db):
        raise HTTPException(status_code=400, detail="Folder does not belong to user")
    message.id = len(messages_db) + 1  # Присваиваем новый ID
    message.created_at = datetime.utcnow()
    messages_db.append(message.dict())
    return message

# Получение всех сообщений в папке
@app.get("/folders/{folder_id}/messages", response_model=List[Message])
def get_messages_in_folder(folder_id: int, current_user: User = Depends(get_current_user)):
    if not any(folder["id"] == folder_id and folder["user_id"] == current_user.id for folder in folders_db):
        raise HTTPException(status_code=400, detail="Folder does not belong to user")
    messages = [msg for msg in messages_db if msg["folder_id"] == folder_id]
    return messages

# Получение сообщения по коду
@app.get("/messages/{message_id}", response_model=Message)
def get_message(message_id: int):
    message = next((m for m in messages_db if m["id"] == message_id), None)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

# Запуск сервиса
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
