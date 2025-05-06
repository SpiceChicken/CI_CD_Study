#!/bin/sh

# wait-for-db.sh
# PostgreSQL, Redis가 올라올 때까지 대기

set -e

host="$DB_HOST"
port="$DB_PORT"
redis_host="$REDIS_HOST"
redis_port="$REDIS_PORT"

echo "[wait-for-db] Waiting for PostgreSQL at $host:$port..."

until pg_isready -h "$host" -p "$port" > /dev/null 2>&1; do
  sleep 1
done

echo "[wait-for-db] PostgreSQL is ready."

echo "[wait-for-db] Waiting for Redis at $redis_host:$redis_port..."

until redis-cli -h "$redis_host" -p "$redis_port" ping | grep -q PONG; do
  sleep 1
done

echo "[wait-for-db] Redis is ready."
