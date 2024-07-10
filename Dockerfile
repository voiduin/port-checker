# Use the official Python image as the base
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Set an environment variable for Flask
ENV FLASK_APP=app.py

# Start Gunicorn with our application on port 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
