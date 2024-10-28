FROM --platform=$TARGETPLATFORM python:3.9-slim

LABEL org.opencontainers.image.source = "https://github.com/probablyjassin/bot-mk8dx-rewrite"

# Install Chrome and dependencies for both architectures
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Add volume for data
VOLUME /app/data

CMD ["python", "-u", "main.py"]
