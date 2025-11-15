# Dockerfile para LoRa P2P Chat Web Server

FROM python:3.11-slim

# Metadata
LABEL maintainer="Tekroy Desarrollos"
LABEL description="LoRa P2P Chat Web Application"
LABEL version="2.0.0"

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para pyserial y USB
RUN apt-get update && apt-get install -y \
    gcc \
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements-web.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements-web.txt

# Copiar código de la aplicación
COPY web_server.py .
COPY serial_comm.py .
COPY static/ ./static/

# Copiar scripts de diagnóstico y testing (opcionales)
COPY test_*.py ./

# Exponer puerto
EXPOSE 8000

# Variable de entorno
ENV PYTHONUNBUFFERED=1

# Comando de inicio
CMD ["uvicorn", "web_server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
