# Use Python 3.10 slim base image
FROM python:3.10-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory inside the container
WORKDIR /app

# Install necessary system packages including GEOS for Shapely
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the Rasa server port
EXPOSE 5005

# Default command to run the Rasa server
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--port", "5005"]
