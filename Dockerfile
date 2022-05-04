FROM python:3.9.5-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV API_KEY API_KEY
ENV MODE MODE

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /bot
COPY . /bot


VOLUME ["/bot/data"]

RUN adduser -u 5678 --disabled-password --gecos "" botuser && chown -R botuser /bot
USER botuser


CMD ["python3", "bot.py"]