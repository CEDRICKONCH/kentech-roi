FROM python:3.11-slim

# Dépendances système minimales (pour PyMySQL + ReportLab)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances Python en premier (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
