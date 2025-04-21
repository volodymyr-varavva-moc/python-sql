#!/bin/bash
set -e

echo "Starting NL2SQL Application..."

# Перевірка наявності директорії для даних
if [ ! -d "/app/data" ]; then
    mkdir -p /app/data
    chmod 777 /app/data
    echo "Created data directory with full permissions"
fi

# Покажемо поточні змінні середовища (без конфіденційних даних)
echo "Environment variables:"
echo "LLM_PROVIDER: $LLM_PROVIDER"
echo "DATABASE_URL: $DATABASE_URL"
echo "APP_ENV: $APP_ENV"

# Ініціалізація бази даних, якщо вона не існує
echo "Initializing database..."
python -m app.db.init_db

# Перевірка, чи вдалося створити базу даних
if [ ! -f "/app/data/app.db" ] && [ "$DATABASE_URL" = "sqlite:///./data/app.db" ]; then
    echo "Creating empty database file..."
    touch /app/data/app.db
    chmod 666 /app/data/app.db
fi

# Запуск FastAPI серверу у фоновому режимі
echo "Starting API server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info &
API_PID=$!

# Очікування запуску API
echo "Waiting for API to start..."
sleep 5

# Перевірка, що API працює
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "API server failed to start! Check logs for details."
    # Виведемо логи для діагностики
    tail -n 50 /app/data/app.log
else
    echo "API server is running. Starting Streamlit frontend..."
fi

# Запуск Streamlit фронтенду
streamlit run app/frontend/app.py --server.address 0.0.0.0 --server.port 8501

# Якщо Streamlit завершується, зупинити API сервер
echo "Streamlit frontend exited. Stopping API server..."
kill $API_PID
