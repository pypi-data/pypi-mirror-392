FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir django django-filter django-widget-tweaks

# Copy the package
COPY . /app/

# Install django-crud-sundae in development mode
RUN pip install -e .

# Create demo project structure
RUN mkdir -p /demo && \
    cd /demo && \
    django-admin startproject demoproject . && \
    python manage.py startapp articles

WORKDIR /demo

# Copy demo configuration files
COPY docker/demo_setup.py /demo/setup.py

# Run setup script
RUN python setup.py

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
