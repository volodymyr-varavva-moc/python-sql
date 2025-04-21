# NL2SQL Application

This application transforms natural language requests into SQL queries and presents the data on a web UI.

## Features

- Natural language to SQL conversion using LLM (Groq, OpenAI, or LocalAI)
- Validation of LLM-generated queries
- Parameter extraction and template application
- Database querying and result display
- Docker support for one-command deployment

## Швидкий старт з Docker

Найпростіший спосіб запустити додаток - використовувати Docker:

1. Отримайте безкоштовний API ключ від Groq на [console.groq.com](https://console.groq.com/)

2. Створіть директорію для даних і переконайтеся, що у вас є відповідні права:
   ```bash
   mkdir -p data
   chmod 777 data
   ```

3. Створіть файл `.env` в корені проекту:
   ```dotenv
   GROQ_API_KEY=ваш_ключ_groq_тут
   ```

4. Запустіть додаток однією командою:
   ```bash
   docker compose up -d
   ```
   > Примітка: Використовуйте `docker compose` (без дефісу) для сучасних версій Docker.

5. Відкрийте:
   - Веб-інтерфейс (Streamlit): http://localhost:8501
   - API документація: http://localhost:8000/api/v1/docs

6. Для зупинки додатку:
   ```bash
   docker compose down
   ```

7. Якщо у вас є проблеми:
   - Перевірте логи: `docker compose logs`
   - Переконайтеся, що директорія `data` має повні права доступу
   - Переконайтеся, що ви правильно налаштували ключ Groq API

Дані зберігаються в локальній директорії `./data`, тому вони не будуть втрачені при перезапуску контейнера.

Все готово! Тепер ви можете використовувати додаток.

## Ручне встановлення (без Docker)

1. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```

2. Налаштуйте файл `.env`:
   ```
   # Виберіть "groq" (безкоштовно) або "openai"
   LLM_PROVIDER=groq
   # Для Groq
   GROQ_API_KEY=ваш_ключ_groq_тут
   # Для OpenAI (тільки якщо використовуєте OpenAI)
   OPENAI_API_KEY=

   # Налаштування бази даних
   DATABASE_URL=sqlite:///./app.db
   APP_ENV=development
   ```

3. Ініціалізуйте базу даних:
   ```bash
   python app/db/init_db.py
   ```

4. Запустіть додаток:
   ```bash
   # Запустіть API сервер
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # В окремому терміналі запустіть Streamlit фронтенд
   streamlit run app/frontend/app.py
   ```

## Використання

1. Введіть запит природною мовою, наприклад:
   - "Покажи всіх клієнтів"
   - "Знайди замовлення з загальною сумою більше 100"
   - "Покажи клієнтів, які зробили замовлення за останні 7 днів"

2. Додаток:
   - Перетворить ваш запит у SQL за допомогою обраного провайдера LLM
   - Виконає запит до бази даних
   - Покаже вам SQL запит, пояснення та результати
- Free cloud API option using Groq

## LLM Providers

This application supports multiple LLM providers:

### Groq (Recommended for Free Usage)

Groq provides free access to high-quality models with generous rate limits (100 requests/minute on the free tier). Perfect for testing and development.

To use Groq:
1. Sign up for a free account at [console.groq.com](https://console.groq.com/)
2. Create an API key
3. Set `LLM_PROVIDER=groq` and `GROQ_API_KEY=your_key` in your `.env` file

### OpenAI

For production use with OpenAI's models:
1. Get an API key from [platform.openai.com](https://platform.openai.com/)
2. Set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=your_key` in your `.env` file

### LocalAI

For fully local, offline usage:
- Follow the LocalAI setup instructions in the project documentation

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your `.env` file:
   ```
   # Choose one: "groq" (free) or "openai"
   LLM_PROVIDER=groq
   # For Groq
   GROQ_API_KEY=your_groq_api_key_here
   # For OpenAI (only if using OpenAI)
   OPENAI_API_KEY=

   # Database settings
   DATABASE_URL=sqlite:///./app.db
   APP_ENV=development
   ```

3. Initialize the database:
   ```bash
   python app/db/init_db.py
   ```

4. Run the application:
   ```bash
   # Start the API server
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # In a separate terminal, start the Streamlit frontend
   streamlit run app/frontend/app.py
   ```

## Usage

1. Enter a natural language query like:
   - "Show me all customers"
   - "Find orders with total amount greater than 100"
   - "List customers who made orders in the last 7 days"

2. The application will:
   - Convert your query to SQL using the chosen LLM provider
   - Execute the query on the database
   - Show you the SQL query, explanation, and results
- 1:N relationship database schema
- Integration and unit tests with >60% coverage

## Setup

### Option 1: Run with LocalAI (Free, No API Key Required)

1. Make sure you have Docker and Docker Compose installed
2. Download the LocalAI model:
   ```bash
   chmod +x model-download.sh
   ./model-download.sh
   ```
3. Run the application with Docker Compose:
   ```bash
   docker-compose up -d
   ```
4. Access the application:
   - Web UI: http://localhost:8501
   - API: http://localhost:8000/docs

### Option 2: Run with OpenAI API

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file with your OpenAI API key:
   ```
   USE_LOCAL_AI=false
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=sqlite:///./app.db
   APP_ENV=development
   ```
3. Initialize the database:
   ```bash
   python app/db/init_db.py
   ```
4. Run the application:
   ```bash
   # Start the API server
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # In a separate terminal, start the Streamlit frontend
   streamlit run app/frontend/app.py
   ```

## Usage

1. Enter a natural language query like:
   - "Show me all customers"
   - "Find orders with total amount greater than 100"
   - "List customers who made orders in the last 7 days"

2. The application will:
   - Convert your query to SQL
   - Execute the query on the database
   - Show you the SQL query, explanation, and results

## Development

To run tests:
```bash
python run_tests.py
