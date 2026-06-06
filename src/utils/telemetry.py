from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCOTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPOTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from utils.config import settings


def init_telemetry() -> None:
    resource = Resource.create(attributes={SERVICE_NAME: settings.otel_service_name})

    provider = TracerProvider(resource=resource)

    if settings.otel_exporter_otlp_endpoint:
        if settings.otel_exporter_otlp_protocol == "grpc":
            exporter = GRPCOTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
        else:
            exporter = HTTPOTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)

        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
