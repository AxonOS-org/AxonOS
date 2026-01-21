FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY pyproject.toml /app/

RUN pip install -e .

EXPOSE 8000

CMD ["uvicorn", "axonos.api.main:app", "--host", "0.0.0.0", "--port", "8000"]