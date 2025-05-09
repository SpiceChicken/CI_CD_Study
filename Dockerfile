FROM python:3.11-slim

RUN apt-get update && apt-get install -y postgresql-client redis-tools

WORKDIR /app

# Python import 경로 인식 설정
ENV PYTHONPATH=/app

# requirements.txt를 먼저 복사해서 캐시 활용
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# wait-for-db.sh 복사 및 실행 권한 부여
COPY wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

# 전체 앱 복사
COPY . /app/

EXPOSE 8000

# CMD는 docker-compose에서 override되므로 생략 가능
