import importlib
import json
import logging
import os
from typing import Any

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_asyncio_instrumentor = None
try:
    _mod = importlib.import_module("opentelemetry.instrumentation.asyncio")
    _asyncio_instrumentor = getattr(_mod, "AsyncIOInstrumentor", None)
except ImportError:
    _asyncio_instrumentor = None


def init_telemetry(app: FastAPI) -> None:
    service_name = os.getenv(
        "OTEL_SERVICE_NAME",
        "book-library-api",
    )

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "1.0.0",
        }
    )

    provider = TracerProvider(
        resource=resource,
    )

    exporter = OTLPSpanExporter(
        endpoint=os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://tempo:4317",
        ),
        insecure=True,
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)

    HTTPXClientInstrumentor().instrument()

    # Instrument asyncio to capture context across async tasks (best-effort)
    if _asyncio_instrumentor is not None:
        try:
            _asyncio_instrumentor().instrument()
        except Exception:  # pylint: disable=broad-exception-caught
            # best-effort; do not fail app startup if instrumentation isn't available
            pass

    # Ensure log records propagate trace/span identifiers and emit JSON
    try:
        LoggingInstrumentor().instrument(set_logging_format=False)
    except ImportError:
        # non-fatal if logging instrumentation not present
        pass

    class OTelContextFilter(logging.Filter):
        def filter(self, record: Any) -> bool:
            span = trace.get_current_span()
            ctx = None
            if span is not None:
                ctx = span.get_span_context()

            if ctx and ctx.is_valid:
                record.trace_id = format(ctx.trace_id, "032x")
                record.span_id = format(ctx.span_id, "016x")
            else:
                record.trace_id = None
                record.span_id = None

            return True

    class JSONFormatter(logging.Formatter):
        def format(self, record: Any) -> str:
            message = super().format(record)
            log_record = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": message,
                "service.name": service_name,
                "trace_id": getattr(record, "trace_id", None),
                "span_id": getattr(record, "span_id", None),
            }

            # include any extra fields present on the record
            extras = {
                k: v
                for k, v in record.__dict__.items()
                if k not in vars(record.__class__)
                and k
                not in (
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "name",
                    "exc_info",
                    "stack_info",
                    "lineno",
                    "pathname",
                    "filename",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "message",
                )
            }

            if extras:
                log_record.update(extras)

            try:
                return json.dumps(log_record, default=str)
            except TypeError, ValueError:
                return message

    # Configure root logger for structured JSON output (best-effort)
    root_logger = logging.getLogger()
    # Only attach handler if none present to avoid duplicate logs in reloads
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        handler.addFilter(OTelContextFilter())

        root_logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
        root_logger.addHandler(handler)
