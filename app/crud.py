from .database import SessionLocal
from .models import URL
import random, string
import redis
import os

# Redis 연결
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.Redis.from_url(redis_url)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_short_url(original_url: str):
    db = SessionLocal()
    code = generate_code()

    # DB 저장
    db_url = URL(original_url=original_url, short_code=code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # Redis 캐시 저장
    r.set(code, original_url)

    return {"short_url": f"http://localhost:8000/r/{code}"}

def resolve_short_url(code: str):
    # Redis 캐시 먼저 조회
    cached_url = r.get(code)
    if cached_url:
        return {"original_url": cached_url.decode("utf-8")}

    # 없으면 DB 조회
    db = SessionLocal()
    db_url = db.query(URL).filter(URL.short_code == code).first()
    if db_url:
        # Redis에 캐시 저장
        r.set(code, db_url.original_url)

        db_url.clicks += 1
        db.commit()
        return {"original_url": db_url.original_url}

    return {"error": "Not found"}
