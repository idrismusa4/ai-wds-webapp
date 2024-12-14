# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the model and app files
COPY best.pt /app/static/models/best.pt
COPY . /app

# Expose port 8080
EXPOSE 8080

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
