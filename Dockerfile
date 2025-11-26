# Use Python 3.11
FROM python:3.11-slim

# Prevent Python from writing temporary files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn whitenoise

# Copy project files
COPY . /app/

# Collect static files (CSS)
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Run the app using Gunicorn
CMD ["gunicorn", "core_project.wsgi:application", "--bind", "0.0.0.0:8000"]