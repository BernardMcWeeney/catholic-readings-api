# Use the official lightweight Python image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create the data directory for persistent storage
RUN mkdir -p data

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]