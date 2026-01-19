# Use a lightweight Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching speed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

EXPOSE 8080

CMD ["python", "gui.py"]