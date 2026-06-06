## Parent PRD

[<docs/prds/opentelemetry-instrumentation.md>](../../prds/opentelemetry-instrumentation.md)

## What to build

Implement the core logic for initializing the OpenTelemetry SDK. This involves setting up the `TracerProvider`, `Resource`, and `BatchSpanProcessor` to export traces via OTLP.

## Step-by-step implementation plan

1.  Create a new file `src/utils/telemetry.py`.
2.  Import `Settings` from `src/utils/config.py`.
3.  Implement an `init_telemetry()` function.
4.  Inside the function, configure a `Resource` with the service name from `settings.otel_service_name`.
5.  Set up the `OTLPSpanExporter` using the endpoint and protocol from `settings`.
6.  Configure a `BatchSpanProcessor` using this exporter.
7.  Set the global `TracerProvider` to use this processor.
8.  Verify the setup by running a script that calls `init_telemetry()` and ensures no errors are thrown.

## Acceptance criteria

- [x] `src/utils/telemetry.py` exists.
- [x] `init_telemetry()` initializes the global `TracerProvider`.
- [x] The exporter is correctly configured with settings from `src/utils/config.py`.
- [x] No runtime errors occur during initialization.

## Blocked by

- Blocked by [01-update-settings.md](./01-update-settings.md)

## User stories addressed

- User story 5

## Implementation Details

- Created `src/utils/telemetry.py` with `init_telemetry()`.
- Added support for both `grpc` and `http` OpenTelemetry OTLP protocols using `GRPCOTLPSpanExporter` and `HTTPOTLPSpanExporter`.
- Verified error-free initialization via script verification.

