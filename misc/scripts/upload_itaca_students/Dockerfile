FROM python:3.12-alpine

# Instalo Python y dependencias necesarias para poder compilar paquetes de Python
RUN apk add --no-cache openjdk17-jdk openssh-client \ 
    g++ \
    musl-dev \
    python3-dev
    
# Configuro entorno para JPype/tabula
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk
ENV PATH="$JAVA_HOME/bin:$PATH"
ENV LD_LIBRARY_PATH="$JAVA_HOME/lib/server:$LD_LIBRARY_PATH"

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copio el script Python y los requisitos
COPY requirements.txt .
COPY main.py .

# Instalo las librerías Python desde requirements
RUN pip install --no-cache-dir -r requirements.txt