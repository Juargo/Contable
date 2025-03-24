FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar el caché de capas de Docker
COPY backend/requirements.txt .

# Si no existe requirements.txt, crearlo
RUN if [ ! -f requirements.txt ]; then \
    echo "fastapi==0.95.1" > requirements.txt && \
    echo "uvicorn==0.22.0" >> requirements.txt && \
    echo "pandas==2.0.1" >> requirements.txt && \
    echo "numpy==1.24.3" >> requirements.txt && \
    echo "pymysql==1.0.3" >> requirements.txt && \
    echo "sqlalchemy==2.0.12" >> requirements.txt && \
    echo "python-multipart==0.0.6" >> requirements.txt; \
    fi

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend/ .

# Puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
