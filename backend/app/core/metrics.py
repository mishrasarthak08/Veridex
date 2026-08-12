from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

def setup_metrics(app: FastAPI):
    # Initialize Prometheus instrumentator for FastAPI
    instrumentator = Instrumentator()
    
    # Instrument the app and expose the /metrics endpoint
    instrumentator.instrument(app).expose(app, include_in_schema=True)
