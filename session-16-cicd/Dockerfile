FROM python:3.12-slim

WORKDIR /app

# Run as a non-root user
RUN useradd --create-home appuser
COPY app ./app
USER appuser

# The calculator is interactive, so run it with: docker run -it <image>
CMD ["python", "app/calculator.py"]
