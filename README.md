# NL2SQL Application

This application transforms natural language requests into SQL queries and presents the data on a web UI.

## Features

- Natural language to SQL conversion using LLM (Groq, OpenAI, or LocalAI)
- Validation of LLM-generated queries
- Parameter extraction and template application
- Database querying and result display
- Docker support for one-command deployment

## Quick Start with Docker

The easiest way to run the application is using Docker:

1. Get a free API key from Groq at [console.groq.com](https://console.groq.com/)

2. Create a data directory and ensure you have appropriate permissions:
   ```bash
   mkdir -p data
   chmod 777 data
   ```

3. Create a `.env` file in the project root:
   ```dotenv
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. Start the application with a single command:
   ```bash
   docker compose up -d
   ```
   > Note: Use `docker compose` (without hyphen) for modern Docker versions.

5. Open:
   - Web interface (Streamlit): http://localhost:8501
   - API documentation: http://localhost:8000/api/v1/docs

6. To stop the application:
   ```bash
   docker compose down
   ```

7. If you have issues:
   - Check logs: `docker compose logs`
   - Make sure the `data` directory has full access permissions
   - Ensure you've configured the Groq API key correctly

Data is stored in the local `./data` directory, so it won't be lost when restarting the container.

All done! Now you can use the application.

## Manual Installation (without Docker)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the `.env` file:
   ```
   # Choose "groq" (free) or "openai"
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

1. Enter a natural language query, for example:
   - "Show all customers"
   - "Find orders with a total amount greater than 100"
   - "Show customers who made orders in the last 7 days"

2. The application will:
   - Convert your query to SQL using the selected LLM provider
   - Execute the query against the database
   - Show you the SQL query, explanation, and results
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
