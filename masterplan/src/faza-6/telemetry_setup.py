# telemetry/setup.py
from opentelemetry import trace, metrics, baggage
from opentelemetry.exporter.otlp.proto.grpc import (
    trace_exporter, metrics_exporter
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.aiohttp import AioHttpInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import os

def setup_telemetry(service_name: str = "litecrewai"):
    """Initialize OpenTelemetry for the application"""
    
    # Resource info
    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.getenv("VERSION", "0.1.0"),
        "deployment.environment": os.getenv("ENV", "development"),
    })
    
    # Tracing
    tracer_provider = TracerProvider(resource=resource)
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        otlp_exporter = trace_exporter.OTLPSpanExporter()
        tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
    
    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(__name__)
    
    # Metrics
    meter_provider = MeterProvider(resource=resource)
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        otlp_metrics = metrics_exporter.OTLPMetricExporter()
        meter_provider.add_metric_reader(
            PeriodicExportingMetricReader(otlp_metrics)
        )
    
    metrics.set_meter_provider(meter_provider)
    meter = metrics.get_meter(__name__)
    
    # Auto-instrumentation
    FastAPIInstrumentor.instrument()
    AioHttpInstrumentor.instrument()
    SQLAlchemyInstrumentor.instrument()
    
    return tracer, meter