# Use uma imagem oficial do Python como base
FROM python:3.13-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do backend
COPY . .

EXPOSE 5000

# Comando para iniciar o backend com gunicorn
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:5000", "-w", "4"]