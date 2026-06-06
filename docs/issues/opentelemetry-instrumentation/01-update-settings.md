## Parent PRD

[<docs/prds/opentelemetry-instrumentation.md>](../../prds/opentelemetry-instrumentation.md)

## What to build

Update the application's configuration schema to support OpenTelemetry settings. This is the foundation for the entire instrumentation task.

## Step-by-step implementation plan

1.  Modify `src/utils/config.py`.
2.  Add `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`, and `OTEL_EXPORTER_OTLP_PROTOCOL` to the `Settings` class.
3.  Ensure these are loaded from environment variables using `pydantic-settings`.
4.  Verify the changes by checking if the new fields are available in the `settings` object after updating an `.env` file.

## Acceptance criteria

- [x] `Settings` class in `src/utils/config.py` includes `otel_service_name`.
- [x] `Settings` class includes `otel_exporter_otlp_endpoint`.
- [x] `Settings` class includes `otel_exporter_otlp_protocol`.
- [x] Values are correctly loaded from environment variables.

## Blocked by

None - can start immediately

## User stories addressed

- User story 5
