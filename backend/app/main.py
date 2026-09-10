from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./karigar_connect.db")
DATABASE_PATH = DATABASE_URL.removeprefix("sqlite:///")


def db() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    directory = os.path.dirname(DATABASE_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with closing(db()) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('artisan', 'buyer', 'admin')),
                language TEXT NOT NULL DEFAULT 'en',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS otp_challenges (
                phone TEXT PRIMARY KEY,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                material TEXT,
                craft_type TEXT,
                price REAL NOT NULL DEFAULT 0,
                image_url TEXT,
                language TEXT NOT NULL DEFAULT 'en',
                status TEXT NOT NULL DEFAULT 'draft',
                artisan_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES categories(id),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                buyer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL
            );
            """
        )
        columns = {row[1] for row in connection.execute("PRAGMA table_info(users)").fetchall()}
        if "phone" not in columns:
            connection.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_phone_unique ON users(phone) WHERE phone IS NOT NULL")
        for name in ("Textiles", "Pottery", "Woodcraft", "Handicrafts"):
            connection.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))
        connection.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="KarigarConnect API", version="1.0.0", lifespan=lifespan)
origins = [item.strip() for item in os.getenv("CORS_ORIGINS", "*").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=200)
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    password: str = Field(min_length=6, max_length=128)
    role: Literal["artisan", "buyer"]
    language: str = "en"


class LoginRequest(BaseModel):
    email: str | None = None
    phone: str | None = None
    password: str


class OtpRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)


class OtpVerifyRequest(BaseModel):
    phone: str = Field(min_length=7, max_length=20)
    code: str = Field(min_length=4, max_length=8)


class ProductRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = ""
    material: str = ""
    craft_type: str = ""
    price: float = Field(default=0, ge=0)
    image_url: str | None = None
    language: str = "en"
    status: Literal["draft", "published"] = "draft"
    category_id: int | None = None


class EnquiryRequest(BaseModel):
    product_id: int
    message: str = Field(min_length=1, max_length=2000)


class StatusRequest(BaseModel):
    status: Literal["open", "accepted", "closed"]


class CatalogRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    regional_language: str | None = None


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${digest}"


def password_matches(password: str, stored: str) -> bool:
    salt, digest = stored.split("$", 1)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return secrets.compare_digest(actual, digest)


def public_user(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "name": row["name"], "email": row["email"] if row["role"] != "artisan" else None, "phone": row["phone"], "role": row["role"], "language": row["language"], "created_at": row["created_at"]}


def current_user(authorization: str | None = Header(default=None)) -> sqlite3.Row:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Authentication required")
    token = authorization.split(" ", 1)[1].strip()
    with closing(db()) as connection:
        row = connection.execute("SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?", (token,)).fetchone()
    if row is None:
        raise HTTPException(401, "Invalid or expired session")
    return row


def require_role(role: str):
    def dependency(user: sqlite3.Row = Depends(current_user)) -> sqlite3.Row:
        if user["role"] != role and user["role"] != "admin":
            raise HTTPException(403, "This action is not available for your role")
        return user
    return dependency


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "karigarconnect-api"}


@app.post("/api/v1/auth/register", status_code=201)
def register(request: RegisterRequest) -> dict:
    email = request.email.lower().strip() if request.email else None
    phone = normalize_phone(request.phone) if request.phone else None
    if request.role == "artisan" and phone is None:
        raise HTTPException(422, "Artisan accounts require a mobile number")
    if request.role == "buyer" and email is None:
        raise HTTPException(422, "Customer accounts require an email address")
    # Older deployments made email non-null; keep phone-only artisan signup compatible.
    if request.role == "artisan" and email is None:
        email = f"{phone}@artisan.local"
    with closing(db()) as connection:
        try:
            cursor = connection.execute("INSERT INTO users(name,email,phone,password_hash,role,language,created_at) VALUES (?,?,?,?,?,?,?)", (request.name.strip(), email, phone, password_hash(request.password), request.role, request.language, now()))
            connection.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(409, "An account with this email or mobile number already exists")
        user = connection.execute("SELECT * FROM users WHERE id=?", (cursor.lastrowid,)).fetchone()
    return _session_response(user)


@app.post("/api/v1/auth/login")
def login(request: LoginRequest) -> dict:
    if request.phone:
        identity = normalize_phone(request.phone)
        query, value = "phone=?", identity
    elif request.email:
        query, value = "email=?", request.email.lower().strip()
    else:
        raise HTTPException(422, "Provide an email or mobile number")
    with closing(db()) as connection:
        user = connection.execute(f"SELECT * FROM users WHERE {query}", (value,)).fetchone()
    if user is None or not password_matches(request.password, user["password_hash"]):
        raise HTTPException(401, "Mobile number or password is incorrect" if request.phone else "Email or password is incorrect")
    return _session_response(user)


def normalize_phone(phone: str) -> str:
    value = "".join(character for character in phone if character.isdigit() or character == "+")
    if value.startswith("00"):
        value = "+" + value[2:]
    if len(value.lstrip("+")) < 7:
        raise HTTPException(422, "Enter a valid mobile number")
    return value


@app.post("/api/v1/auth/otp/request")
def request_otp(request: OtpRequest) -> dict:
    phone = normalize_phone(request.phone)
    code = f"{secrets.randbelow(1_000_000):06d}"
    with closing(db()) as connection:
        connection.execute("INSERT OR REPLACE INTO otp_challenges(phone,code_hash,expires_at,attempts) VALUES (?,?,?,0)", (phone, password_hash(code), datetime.now(timezone.utc).timestamp() + 300))
        connection.commit()
    response = {"message": "OTP requested. Connect an SMS provider to deliver it."}
    if os.getenv("AUTH_OTP_DEV_MODE", "false").lower() == "true":
        response["dev_code"] = code
    return response


@app.post("/api/v1/auth/otp/verify")
def verify_otp(request: OtpVerifyRequest) -> dict:
    phone = normalize_phone(request.phone)
    with closing(db()) as connection:
        challenge = connection.execute("SELECT * FROM otp_challenges WHERE phone=?", (phone,)).fetchone()
        user = connection.execute("SELECT * FROM users WHERE phone=? AND role='artisan'", (phone,)).fetchone()
        if challenge is None or user is None or float(challenge["expires_at"]) < datetime.now(timezone.utc).timestamp() or challenge["attempts"] >= 5:
            raise HTTPException(401, "OTP is invalid or expired")
        connection.execute("UPDATE otp_challenges SET attempts=attempts+1 WHERE phone=?", (phone,))
        connection.commit()
    if not password_matches(request.code, challenge["code_hash"]):
        raise HTTPException(401, "OTP is invalid or expired")
    return _session_response(user)


def _session_response(user: sqlite3.Row) -> dict:
    token = secrets.token_urlsafe(32)
    with closing(db()) as connection:
        connection.execute("INSERT INTO sessions(token,user_id,created_at) VALUES (?,?,?)", (token, user["id"], now()))
        connection.commit()
    return {"access_token": token, "token_type": "bearer", "user": public_user(user)}


@app.get("/api/v1/auth/me")
def me(user: sqlite3.Row = Depends(current_user)) -> dict:
    return public_user(user)


@app.post("/api/v1/catalog")
def catalog(request: CatalogRequest, user: sqlite3.Row = Depends(require_role("artisan"))) -> dict:
    text = request.text.strip()
    lower = text.lower()
    category = "Textiles" if any(word in lower for word in ("saree", "cloth", "weave", "cotton")) else "Pottery" if any(word in lower for word in ("pot", "clay")) else "Woodcraft" if any(word in lower for word in ("wood", "carve")) else "Handicrafts"
    words = text.split()
    title = " ".join(words[:5]).capitalize()
    return {"title": title, "description": text, "category": category, "material": "cotton" if "cotton" in lower else "", "craft_type": "Handmade", "warnings": [], "source": "local"}


def product_dict(row: sqlite3.Row) -> dict:
    result = dict(row)
    result["price"] = float(result["price"])
    return result


@app.get("/api/v1/products")
def products(search: str | None = Query(default=None), mine: bool = False, user: sqlite3.Row | None = Depends(lambda authorization=Header(default=None): _optional_user(authorization))) -> list[dict]:
    query = "SELECT p.*, c.name AS category_name, u.name AS artisan_name FROM products p LEFT JOIN categories c ON c.id=p.category_id JOIN users u ON u.id=p.artisan_id WHERE p.status='published'"
    values: list[object] = []
    if mine and user:
        query = query.replace("WHERE p.status='published'", "WHERE p.artisan_id=?")
        values.append(user["id"])
    if search:
        query += " AND (p.title LIKE ? OR p.description LIKE ? OR p.material LIKE ?)"
        pattern = f"%{search}%"
        values.extend([pattern, pattern, pattern])
    with closing(db()) as connection:
        return [product_dict(row) for row in connection.execute(query + " ORDER BY p.created_at DESC", values).fetchall()]


def _optional_user(authorization: str | None) -> sqlite3.Row | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    with closing(db()) as connection:
        return connection.execute("SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?", (token,)).fetchone()


@app.get("/api/v1/products/{product_id}")
def product(product_id: int) -> dict:
    with closing(db()) as connection:
        row = connection.execute("SELECT p.*, c.name AS category_name, u.name AS artisan_name FROM products p LEFT JOIN categories c ON c.id=p.category_id JOIN users u ON u.id=p.artisan_id WHERE p.id=?", (product_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Product not found")
    return product_dict(row)


@app.post("/api/v1/products", status_code=201)
def create_product(request: ProductRequest, user: sqlite3.Row = Depends(require_role("artisan"))) -> dict:
    category_id = request.category_id
    with closing(db()) as connection:
        if category_id is None:
            category_id = connection.execute("SELECT id FROM categories WHERE name=?", ("Handicrafts",)).fetchone()["id"]
        cursor = connection.execute("INSERT INTO products(title,description,material,craft_type,price,image_url,language,status,artisan_id,category_id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (request.title, request.description, request.material, request.craft_type, request.price, request.image_url, request.language, request.status, user["id"], category_id, now()))
        connection.commit()
        row = connection.execute("SELECT p.*, c.name AS category_name, u.name AS artisan_name FROM products p LEFT JOIN categories c ON c.id=p.category_id JOIN users u ON u.id=p.artisan_id WHERE p.id=?", (cursor.lastrowid,)).fetchone()
    return product_dict(row)


@app.patch("/api/v1/products/{product_id}")
def update_product(product_id: int, request: ProductRequest, user: sqlite3.Row = Depends(require_role("artisan"))) -> dict:
    with closing(db()) as connection:
        row = connection.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Product not found")
        if row["artisan_id"] != user["id"] and user["role"] != "admin":
            raise HTTPException(403, "You can only edit your own products")
        connection.execute("UPDATE products SET title=?,description=?,material=?,craft_type=?,price=?,image_url=?,language=?,status=?,category_id=? WHERE id=?", (*request.model_dump(exclude={"category_id"}).values(), request.category_id or row["category_id"], product_id))
        connection.commit()
        updated = connection.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    return product_dict(updated)


@app.post("/api/v1/enquiries", status_code=201)
def create_enquiry(request: EnquiryRequest, user: sqlite3.Row = Depends(require_role("buyer"))) -> dict:
    with closing(db()) as connection:
        if connection.execute("SELECT id FROM products WHERE id=? AND status='published'", (request.product_id,)).fetchone() is None:
            raise HTTPException(404, "Published product not found")
        cursor = connection.execute("INSERT INTO enquiries(message,product_id,buyer_id,created_at) VALUES (?,?,?,?)", (request.message, request.product_id, user["id"], now()))
        connection.commit()
        row = connection.execute("SELECT e.*, p.title AS product_title, u.name AS buyer_name FROM enquiries e JOIN products p ON p.id=e.product_id JOIN users u ON u.id=e.buyer_id WHERE e.id=?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@app.get("/api/v1/enquiries")
def enquiries(user: sqlite3.Row = Depends(current_user)) -> list[dict]:
    query = "SELECT e.*, p.title AS product_title, b.name AS buyer_name, a.name AS artisan_name FROM enquiries e JOIN products p ON p.id=e.product_id JOIN users b ON b.id=e.buyer_id JOIN users a ON a.id=p.artisan_id WHERE e.buyer_id=?" if user["role"] == "buyer" else "SELECT e.*, p.title AS product_title, b.name AS buyer_name, a.name AS artisan_name FROM enquiries e JOIN products p ON p.id=e.product_id JOIN users b ON b.id=e.buyer_id JOIN users a ON a.id=p.artisan_id WHERE p.artisan_id=?"
    with closing(db()) as connection:
        return [dict(row) for row in connection.execute(query + " ORDER BY e.created_at DESC", (user["id"],)).fetchall()]


@app.patch("/api/v1/enquiries/{enquiry_id}")
def update_enquiry(enquiry_id: int, request: StatusRequest, user: sqlite3.Row = Depends(require_role("artisan"))) -> dict:
    with closing(db()) as connection:
        row = connection.execute("SELECT e.*, p.artisan_id FROM enquiries e JOIN products p ON p.id=e.product_id WHERE e.id=?", (enquiry_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Enquiry not found")
        if row["artisan_id"] != user["id"] and user["role"] != "admin":
            raise HTTPException(403, "You can only manage enquiries for your products")
        connection.execute("UPDATE enquiries SET status=? WHERE id=?", (request.status, enquiry_id))
        connection.commit()
    return {"id": enquiry_id, "status": request.status}


@app.get("/api/v1/categories")
def categories() -> list[dict]:
    with closing(db()) as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM categories ORDER BY name").fetchall()]


@app.on_event("startup")
def startup() -> None:
    init_db()