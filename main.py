from fastapi import FastAPI, HTTPException, Response, Request, Header
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import uuid
import time
import datetime
import re
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

app = FastAPI(title="КР2: Технологии разработки серверных приложений")


SECRET_KEY = "super-secret-key-for-assignment"
serializer = URLSafeTimedSerializer(SECRET_KEY)


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = Field(None, gt=0, description="Должно быть положительным целым числом")
    is_subscribed: Optional[bool] = False

@app.post("/create_user", tags=["Задание 3.1"])
def create_user(user: UserCreate)
    return user.model_dump()


sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}
]

@app.get("/product/{product_id}", tags=["Задание 3.2"])
def get_product(product_id: int):
    for p in sample_products:
        if p["product_id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/products/search", tags=["Задание 3.2"])
def search_products(keyword: str, category: Optional[str] = None, limit: int = 10)
    results = []
    kw_lower = keyword.lower()
    for p in sample_products:
        if kw_lower in p["name"].lower():
            if category is None or category.lower() == p["category"].lower():
                results.append(p)
        if len(results) >= limit:
            break
    return results


VALID_USERS = {"user123": "password123", "admin": "adminpass"}

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login", tags=["Задания 5.1-5.3"])
def login(data: LoginData, response: Response):
    if VALID_USERS.get(data.username) != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(uuid.uuid4())
    current_ts = int(time.time())
    

    payload = f"{user_id}.{current_ts}"
    token = serializer.dumps(payload)

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,  
        max_age=300,  
        samesite="lax"
    )
    return {"message": "Login successful", "user_id": user_id}

def _verify_session(token: str) -> tuple[dict, bool]
    try:

        payload = serializer.loads(token, max_age=300)
        user_id, cookie_ts_str = payload.split(".")
        cookie_ts = int(cookie_ts_str)
        now = int(time.time())
        elapsed = now - cookie_ts

        if elapsed >= 300:
            raise HTTPException(status_code=401, detail="Session expired")

        needs_update = 180 <= elapsed < 300
        return {"user_id": user_id, "username": "user123"}, needs_update

    except SignatureExpired:
        raise HTTPException(status_code=401, detail="Session expired")
    except (BadSignature, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid session")

@app.get("/user", tags=["Задания 5.1-5.3"])
@app.get("/profile", tags=["Задания 5.1-5.3"])
def get_protected_user(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_data, needs_update = _verify_session(token)

    if needs_update:
        new_ts = int(time.time())
        new_payload = f"{user_data['user_id']}.{new_ts}"
        new_token = serializer.dumps(new_payload)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            max_age=300,
            samesite="lax"
        )
    return user_data


class CommonHeaders(BaseModel):
    user_agent: str = Header(..., alias="User-Agent")
    accept_language: str = Header(..., alias="Accept-Language")

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        pattern = r'^[a-zA-Z\-]{2,}(?:,[a-zA-Z\-]{2,}(?:;q=[0-9]\.[0-9])?)*$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Accept-Language format. Expected: "en-US,en;q=0.9"')
        return v

@app.get("/headers", tags=["Задания 5.4-5.5"])
def get_headers(headers: CommonHeaders):
    return {"User-Agent": headers.user_agent, "Accept-Language": headers.accept_language}

@app.get("/info", tags=["Задания 5.4-5.5"])
def get_info(headers: CommonHeaders, response: Response:
    response.headers["X-Server-Time"] = datetime.datetime.now().isoformat()
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }
