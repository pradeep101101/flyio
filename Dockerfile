# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to ensure non-interactive frontend for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies identified from replit.nix
# ffmpeg is essential for moviepy
# imagemagick and libgl1-mesa-glx are good to include as moviepy might use them
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    imagemagick \
    libgl1-mesa-glx \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This includes main.py, and the 'templates' folder (implicitly)
# If your index.html is in a 'templates' folder, make sure it's copied.
# Assuming index.html is in a 'templates' subfolder:
COPY templates/ ./templates/
COPY main.py .
# If you have a 'static' folder for CSS/JS, copy it too:
# COPY static/ ./static/

# Make port 8080 available (Fly.io will map to this)
ENV PORT 8080
EXPOSE 8080

# Command to run your application using Gunicorn
# Ensure 'app' is the name of your Flask application instance in main.py
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "--workers", "1", "--threads", "4", "--timeout", "180", "main:app"]
