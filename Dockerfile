FROM python:3.11-slim
FROM python:3.10-slim

WORKDIR /app

# Встановлення необхідних системних пакетів
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Створення директорії для даних
RUN mkdir -p /app/data

# Копіювання requirements для кращого кешування
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду додатку
COPY . .

# Налаштування середовища
ENV PYTHONPATH=/app
ENV APP_ENV=production
ENV DATABASE_URL=sqlite:///./data/app.db

# Встановлення прав на скрипт запуску
RUN chmod +x /app/start.sh

# Відкриття портів
EXPOSE 8000
EXPOSE 8501

# Запуск додатку
CMD ["/app/start.sh"]
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create directory for the database
RUN mkdir -p /app/data

# Set environment variables
ENV DATABASE_URL=sqlite:////app/data/app.db
ENV OPENAI_API_KEY=dummy_key_for_build

# Copy application code
COPY . .

# Create startup script for database initialization and app start
RUN echo '#!/bin/bash\n\
# Initialize the database\n\
python app/db/init_db.py\n\
\n\
# Start the API server\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000 & \n\
# Start the Streamlit frontend\n\
streamlit run app/frontend/app.py --server.port 8501 --server.address 0.0.0.0\n\
' > /app/start.sh \
&& chmod +x /app/start.sh

# Expose ports for API and Streamlit
EXPOSE 8000 8501

# Run the application
CMD ["/app/start.sh"]
