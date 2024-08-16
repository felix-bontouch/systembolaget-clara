# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /usr/src/app

# Install system dependencies for PostgreSQL and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the PYTHONPATH to the working directory
ENV PYTHONPATH=/usr/src/app

# Copy the FastAPI code and the Streamlit app
COPY ./api ./api
COPY ./app ./app
COPY ./config ./config

# Expose the ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# Run both FastAPI and Streamlit applications
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload & streamlit run app/app.py --server.port 8501 --server.address 0.0.0.0"]
