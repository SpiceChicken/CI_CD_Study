#!/bin/sh

# PostgreSQL 준비 대기
until pg_isready -h db -p 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done
echo "PostgreSQL is ready!"

# Redis 준비 대기
until redis-cli -h redis -p 6379 ping | grep -q PONG; do
  echo "Waiting for Redis..."
  sleep 2
done
echo "Redis is ready!"
