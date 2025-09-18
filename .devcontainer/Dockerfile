FROM mcr.microsoft.com/devcontainers/python:3.11

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Установка Wine для tool1cd (Windows инструменты)
RUN apt-get update && apt-get install -y \
    wine \
    winetricks \
    && rm -rf /var/lib/apt/lists/*

# Настройка Wine
RUN winecfg

# Установка Python зависимостей
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# Создание рабочей директории
WORKDIR /workspaces/heroes-1c-extractor

# Настройка переменных окружения
ENV PYTHONPATH="/workspaces/heroes-1c-extractor/src:/workspaces/heroes-1c-extractor/tests"
ENV PYTHONUNBUFFERED=1

# Установка Jupyter для анализа данных
RUN pip install jupyter notebook jupyterlab

# Создание пользователя vscode
RUN useradd -m -s /bin/bash vscode && \
    usermod -aG sudo vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Переключение на пользователя vscode
USER vscode

# Настройка Git
RUN git config --global init.defaultBranch main

# Команда по умолчанию
CMD ["/bin/bash"]
