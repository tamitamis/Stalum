# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Collect static files (CSS/JS) so they work in production
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Run the application using Gunicorn (Production Server)
CMD ["gunicorn", "core_project.wsgi:application", "--bind", "0.0.0.0:8000"]