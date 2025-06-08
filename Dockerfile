FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Expose port for FastAPI
EXPOSE 8000

# Default command runs the FastAPI server
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternative commands:
# For REST CLI: CMD ["python", "-m", "src.rest.rest_main"]
# For GraphQL CLI: CMD ["python", "-m", "src.graphql.graphql_main"]
# For benchmark: CMD ["python", "-m", "src.benchmark.benchmark_runner"]