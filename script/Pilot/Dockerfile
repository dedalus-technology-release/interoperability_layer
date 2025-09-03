# Usa un'immagine Python di base
FROM python:3.12

# Installa curl
RUN apt-get update && apt-get install -y curl

# Imposta la directory di lavoro nel contenitore
WORKDIR /app

# Copia la cartella "script/Danish Pilot" nella directory di lavoro del contenitore
COPY script/Pilot/ /app/

# Comando per eseguire lo script quando il contenitore viene avviato
CMD ["python", "read_script.py"]