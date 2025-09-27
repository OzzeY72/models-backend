# FastAPI Backend

## Environment Variables

Before running the app, configure the following environment variables:

- `SECRET_TOKEN` – a secret key used to authenticate requests between the backend and client apps.  
- `REDIS_HOST` – Redis server hostname or IP.  
- `REDIS_PORT` – Redis server port (default: `6379`).  
- `REDIS_USERNAME` – Redis username (optional, depends on your Redis setup).  
- `REDIS_PASSWORD` – Redis password (optional, depends on your Redis setup).  
- `SQLALCHEMY_DATABASE_URL` – SQLAlchemy database connection string, e.g.:  
  - PostgreSQL: `postgresql+psycopg2://user:password@localhost:5432/dbname`

## Run without Docker

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
    ```
2. Set environment variables (example for Linux/macOS):
    ```bash
    export SECRET_TOKEN="mysecret"
    export REDIS_HOST="localhost"
    export REDIS_PORT="6379"
    export REDIS_USERNAME="user"
    export REDIS_PASSWORD="password"
    export SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/mydb"
    ```

3. Run database migrations:
    ```bash
    alembic revision --autogenerate -m "Init"
    alembic upgrade head
    ```

4. Start the FastAPI app:
    ```bash
    fastapi run ./main.py
    ```
    
    By default, the server will be available at: http://localhost:8000