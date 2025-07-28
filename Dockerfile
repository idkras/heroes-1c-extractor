FROM ubuntu:20.04

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование утилиты ctool1cd
COPY ctool1cd /app/ctool1cd
RUN chmod +x /app/ctool1cd

# Создание точки входа
ENTRYPOINT ["/app/ctool1cd"] 