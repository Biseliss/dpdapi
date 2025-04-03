import os
import secrets
import string
import random
import hashlib
from datetime import datetime, timedelta
from fastapi import UploadFile
from typing import Optional

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def generate_token_hex(length=64) -> str:
    return secrets.token_hex(length // 2)  # length=32 → 64 hex chars

def generate_code(length=6) -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_future_time(minutes=30) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)

def store_file_in_directory(
    file: UploadFile,
    base_dir: str = "uploads"
) -> str:
    ext = None
    if file.content_type == "image/jpeg":
        ext = ".jpg"
    elif file.content_type == "image/png":
        ext = ".png"
    else:
        # другие типы (в этом приложении тут может быть только гиф). так же успешно может отсутствовать
        original_ext = os.path.splitext(file.filename)[1]

    os.makedirs(base_dir, exist_ok=True)
    while True: # генерация уникального имени файла
        random_name = generate_token_hex(12)  # 24 hex-символа
        filename = random_name + ext
        file_path = os.path.join(base_dir, filename)
        if not os.path.exists(file_path):
            break

    # 3) Сохраняем файл
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return filename

#эта функция обрезает строки, которые длиннее указанной длины
# TODO сделать более читаемой
def cut_string(string, mx, points=True, points_text=" ...", sep=" "):
    p = len(points_text) if points else 0
    if (len(string) > mx):
        string = string[:mx-p]
        string = sep.join(string.split(sep)[:-1])
        if (points):
            string += points_text
    return string
