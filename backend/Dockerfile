FROM python:3.12-slim

WORKDIR /app

# 1) zależności z requirements.txt (cache działa, gdy kod się zmienia)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) kod aplikacji
COPY app ./app
COPY tests ./tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
