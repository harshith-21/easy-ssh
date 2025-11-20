FROM python:3.11-slim

# Install kubectl and system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set Django settings module
ENV DJANGO_SETTINGS_MODULE=easy_ssh.settings

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 9000

# Run migrations and start server
CMD python manage.py makemigrations && python manage.py migrate && daphne -b 0.0.0.0 -p 9000 easy_ssh.asgi:application

