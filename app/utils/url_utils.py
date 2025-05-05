# app/utils/url_utils.py

import random
import string

def generate_short_path(length: int = 6) -> str:
    """랜덤한 문자열로 단축된 URL 경로를 생성"""
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    short_path = ''.join(random.choices(characters, k=length))
    return short_path
