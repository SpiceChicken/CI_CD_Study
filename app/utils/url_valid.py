import requests

def is_url_valid(url: str) -> bool:
    try:
        response = requests.get(url, timeout=5)  # 5초 타임아웃
        return response.status_code == 200  # HTTP 200 상태 코드만 유효한 것으로 간주
    except requests.exceptions.RequestException:
        return False