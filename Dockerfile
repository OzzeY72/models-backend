FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SECRET_TOKEN=""
ENV REDIS_HOST=""
ENV REDIS_PORT=""
ENV REDIS_USERNAME=""
ENV REDIS_PASSWORD=""
ENV SQLALCHEMY_DATABASE_URL=""

CMD alembic revision --autogenerate -m "Init" && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
