# Folosim Python 3.11 (mai nou, mai stabil, fara warning-uri)
FROM python:3.11-slim

WORKDIR /app

# Copiem fisierele
COPY requirements.txt .
COPY server.py .

# Instalam dependintele si fortam upgrade la ultima versiune de google-generativeai
# ca sa fim siguri ca recunoaste modelele "flash"
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 5555

ENV PYTHONUNBUFFERED=1

CMD ["python", "server.py"]