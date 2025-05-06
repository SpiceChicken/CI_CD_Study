FROM python:3.11-slim

RUN apt-get update && apt-get install -y postgresql-client redis-tools

WORKDIR /app

# wait-for-db.sh 먼저 복사
COPY wait-for-db.sh /app/wait-for-db.sh
RUN chmod +x /app/wait-for-db.sh

# 나머지 복사
COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]