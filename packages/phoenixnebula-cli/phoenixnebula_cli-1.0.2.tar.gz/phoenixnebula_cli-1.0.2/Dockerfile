FROM python:3.11-slim

LABEL maintainer="Salih <salihyilboga98@gmail.com>"
LABEL description="Phoenixnebula - A feature-rich, customizable Unix shell"

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["phoenixnebula"]