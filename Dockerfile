FROM postgres:16-alpine as postgres

# Create a custom PostgreSQL configuration
RUN echo "listen_addresses='*'" >> /usr/local/share/postgresql/postgresql.conf

FROM python:3.11-slim

# Install system dependencies including PostgreSQL client and locales
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    locales \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen

# Set the locale environment variables
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create data directory
RUN mkdir -p data

EXPOSE 5000

CMD ["python", "app.py"] 