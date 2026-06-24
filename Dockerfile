# Utilizando Python 3.12 (Estável)
FROM python:3.12-slim

# Define variáveis de ambiente para evitar arquivos .pyc e logs em buffer
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para o psycopg2 e netcat (nc)
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    gcc \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o código necessário
COPY ./core /app/core
COPY ./domains /app/domains
COPY ./infrastructure /app/infrastructure
COPY ./project /app/project
COPY ./shared /app/shared
COPY ./templates /app/templates
COPY ./media /app/media
COPY ./manage.py /app/manage.py
COPY ./scripts /scripts

# Garante que o script seja executável
RUN chmod +x /scripts/command.sh

# Expõe a porta 8000
EXPOSE 8000

# Define o comando de inicialização
CMD ["/scripts/command.sh"]
