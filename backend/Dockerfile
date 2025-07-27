# Use official Python
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy backend code
COPY backend/ /app/

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Command to run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
