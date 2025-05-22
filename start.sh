#!/bin/bash
echo "Starting FastAPI server at port 8600..."
uvicorn main:app --reload --port 8600
