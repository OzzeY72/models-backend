FROM node:20 AS frontend-builder

WORKDIR /frontend

COPY workwithus-mini/package*.json ./

RUN npm install

COPY workwithus-mini/ .

RUN npm run build

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

EXPOSE 8000
# alembic revision --autogenerate -m "Init"
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
