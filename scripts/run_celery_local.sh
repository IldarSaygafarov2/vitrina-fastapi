#!/usr/bin/env bash
# Запуск Redis и Celery (worker + beat) локально

set -e
cd "$(dirname "$0")/.."

REDIS_CONTAINER="vitrina-redis-local"
REDIS_PORT=6379

# Проверка .env
if [ ! -f .env ]; then
  echo "Создайте .env из .env.dist и заполните переменные"
  exit 1
fi

# Экспорт Redis для локального запуска
export REDIS_BROKER_URL="${REDIS_BROKER_URL:-redis://localhost:${REDIS_PORT}/0}"
export REDIS_BACKEND_URL="${REDIS_BACKEND_URL:-redis://localhost:${REDIS_PORT}/0}"

start_redis() {
  if docker ps -q -f "name=${REDIS_CONTAINER}" 2>/dev/null | grep -q .; then
    echo "Redis уже запущен (${REDIS_CONTAINER})"
    return
  fi
  if docker ps -aq -f "name=${REDIS_CONTAINER}" 2>/dev/null | grep -q .; then
    docker start "$REDIS_CONTAINER"
  else
    docker run -d --name "$REDIS_CONTAINER" -p "${REDIS_PORT}:6379" redis:7-alpine
  fi
  echo "Ожидание Redis..."
  until docker exec "$REDIS_CONTAINER" redis-cli ping 2>/dev/null | grep -q PONG; do
    sleep 1
  done
  echo "Redis запущен"
}

stop_redis() {
  docker stop "$REDIS_CONTAINER" 2>/dev/null || true
}

cleanup() {
  echo ""
  echo "Остановка Celery worker и beat..."
  [ -n "${WORKER_PID:-}" ] && kill $WORKER_PID 2>/dev/null || true
  [ -n "${BEAT_PID:-}" ] && kill $BEAT_PID 2>/dev/null || true
  echo "Остановка Redis..."
  stop_redis
  exit 0
}

trap cleanup SIGINT SIGTERM

start_redis

echo "Запуск Celery worker и beat..."
celery -A celery_tasks.app worker --loglevel=info &
WORKER_PID=$!
celery -A celery_tasks.app beat --loglevel=info &
BEAT_PID=$!

echo "Celery worker (PID $WORKER_PID) и beat (PID $BEAT_PID) запущены"
echo "Нажмите Ctrl+C для остановки"
wait
