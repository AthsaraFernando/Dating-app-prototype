# Use the official Python image as the base
FROM python:3.13

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    APP_DIR=/app

# Set the working directory inside the container
WORKDIR $APP_DIR

# Copy the project files from the local directory (current directory) to the container
COPY . $APP_DIR

# Install dependencies if a requirements.txt file exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Expose a port (adjust based on the app configuration)
EXPOSE 5000

# Command to run the application (update if different)
CMD ["python", "app.py"]
