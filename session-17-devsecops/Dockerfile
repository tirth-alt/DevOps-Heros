FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Run as a non-root user (numeric id so Kubernetes can verify runAsNonRoot)
RUN useradd --uid 10001 --no-create-home appuser
USER 10001

EXPOSE 5001

CMD ["python", "app/app.py"]
