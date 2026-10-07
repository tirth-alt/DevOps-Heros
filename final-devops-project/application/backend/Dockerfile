FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

# Run as a non-root user with a fixed numeric id (Kubernetes can verify runAsNonRoot)
RUN useradd --uid 10001 --no-create-home appuser
USER 10001

EXPOSE 8000

# Apply database migrations, then start the API.
# In Kubernetes the migrations run in a separate Job, and this command is overridden.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
