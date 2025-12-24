FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set basic Django settings for build
ENV SECRET_KEY=build-time-key
ENV DEBUG=False
ENV ALLOWED_HOSTS=localhost,127.0.0.1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Run migrations
RUN python manage.py migrate

# Skip collectstatic for now since there are no static files
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD gunicorn stripe_payments.wsgi:application --bind 0.0.0.0:$PORT
