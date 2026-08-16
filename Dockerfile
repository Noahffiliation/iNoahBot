FROM python:3.14.7-slim-bookworm

RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py ./

USER appuser

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
