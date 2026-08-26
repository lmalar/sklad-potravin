FROM python:3.11-slim

WORKDIR /app

# Zkopírování seznamu závislostí a jejich instalace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Zkopírování samotného kódu a šablon vzhledu
COPY app.py .
COPY templates/ templates/

# Vytvoření složky pro databázi (která se pak přes docker-compose připojí ven)
RUN mkdir data

# Otevření komunikačního portu
EXPOSE 5000

# Příkaz, kterým se aplikace po startu kontejneru spustí
CMD ["python", "app.py"]