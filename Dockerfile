# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy requirements first to improve caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

# Expose the FastAPI port
EXPOSE 8000
RUN pip install python-multipart

# Run FastAPI with live reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
