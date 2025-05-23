#!/bin/bash

echo "Starting FastAPI server at port 8600..."

# Activate virtual environment
source venv/bin/activate

# Define certificate and key file paths
CERT_FILE="/home/demoConverge/urRobot/babylon-rosbridge/ur-babylon-main/sslfile/cert.pem"
KEY_FILE="/home/demoConverge/urRobot/babylon-rosbridge/ur-babylon-main/sslfile/key.pem"

# Run FastAPI with HTTPS
uvicorn main:app --reload --host 0.0.0.0 --port 8600 --ssl-keyfile "$KEY_FILE" --ssl-certfile "$CERT_FILE"

# Or with HTTP
# uvicorn main:app --reload --host 0.0.0.0 --port 8600
