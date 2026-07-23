#!/bin/bash

# Veridex Chaos Engineering Test Script
# This script simulates infrastructure turbulence to verify Celery and Istio retry logic.

echo "=========================================="
echo "    Veridex Chaos Engineering Test        "
echo "=========================================="
echo ""

if ! command -v docker &> /dev/null
then
    echo "Error: Docker could not be found. Please install Docker to run chaos tests."
    exit 1
fi

echo "[1/4] Ensuring services are running..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "[2/4] Triggering a background ingestion job (simulating heavy load)..."
# Using the CLI SDK if available
if command -v veridex &> /dev/null
then
    veridex knowledge sync --type filesystem --config '{"directory_path": "./"}' &
else
    echo "Warning: veridex CLI not installed globally, skipping actual job submission."
fi

echo ""
echo "[3/4] Initiating Chaos - Stopping Redis broker mid-flight!"
docker compose -f docker-compose.prod.yml stop redis
echo "Redis stopped. Workers should now be throwing connection errors and entering exponential backoff..."
sleep 10

echo ""
echo "[4/4] Restoring Chaos - Starting Redis broker..."
docker compose -f docker-compose.prod.yml start redis
echo "Redis started. Workers should automatically reconnect and resume the ingestion job without data loss."
sleep 5

echo ""
echo "Chaos Test Complete!"
echo "Please verify the worker logs to confirm the Celery max_retries and backoff succeeded:"
echo "  docker compose -f docker-compose.prod.yml logs worker"
