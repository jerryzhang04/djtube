# Use the official Python image from Docker Hub
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Set the environment variable to allow Flask to run inside the container
ENV FLASK_RUN_HOST 0.0.0.0

# Command to run your application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
