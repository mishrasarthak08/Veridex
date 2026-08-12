import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from fastapi import FastAPI

def setup_telemetry(app: FastAPI = None):
    # Set up TracerProvider
    resource = Resource.create({
        SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "veridex-backend")
    })
    
    provider = TracerProvider(resource=resource)
    
    # Configure OTLP Exporter (Defaults to http://localhost:4317 if not set)
    # Using insecure=True for internal docker network
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI if app is provided
    if app:
        FastAPIInstrumentor.instrument_app(app)
        
    # Instrument Celery
    CeleryInstrumentor().instrument()
