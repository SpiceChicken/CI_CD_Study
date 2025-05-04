# 베이스 이미지 선택
FROM python:3.11-slim

# 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y postgresql-client redis-tools

# FastAPI 애플리케이션 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# wait-for-db.sh 스크립트 복사
COPY wait-for-db.sh /app/
RUN chmod +x /app/wait-for-db.sh

# 애플리케이션 파일 복사
COPY . /app/

# 포트 노출
EXPOSE 8000

# 기본 실행 명령 (docker-compose.yml에서 커맨드 설정됨)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]