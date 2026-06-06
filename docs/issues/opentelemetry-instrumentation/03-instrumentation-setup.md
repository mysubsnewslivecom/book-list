## Parent PRD

[<docs/prds/opentelemetry-instrumentation.md>](../../prds/opentelemetry-instrumentation.md)

## What to build

Configure the OpenTelemetry instrumentors for FastAPI and SQLAlchemy within the telemetry initialization logic. This ensures that HTTP requests and database queries are automatically captured as spans.

## Step-by-step implementation plan

1.  Modify the `init_telemetry()` function in `src/utils/telemetry.py`.
2.  Add instrumentation for FastAPI using `FastApiInstrumentor.instrument_app(app)`. Note: Since `app` might not be available at initialization time, consider how to pass the app instance or use a more flexible approach.
3.  Add instrumentation for SQLAlchemy using `SQLAlchemyInstrumentor().instrument(engine=...)`. You will need to retrieve the engine from the application's database utility.
4.  Verify that both instrumentors are correctly configured and can be initialized without errors.

## Acceptance criteria

- [x] `FastApiInstrumentor` is configured for the application.
- [x] `SQLAlchemyInstrumentor` is configured for the database engine.
- [x] No errors occur during the instrumentation setup process.

## Blocked by

- Blocked by [02-telemetry-init.md](./02-telemetry-init.md)

## User stories addressed

- User story 1
- User story 2

## Implementation Details

- Imported `FastAPIInstrumentor` and `SQLAlchemyInstrumentor` in `src/utils/telemetry.py`.
- Configured SQLAlchemy engine instrumentation.
- Added `app` parameter to `init_telemetry()` and configured FastAPI application instrumentation.
- Added `opentelemetry-instrumentation-sqlalchemy` to `pyproject.toml` dependencies and resolved lock file.

