## Parent PRD

[<docs/prds/opentelemetry-instrumentation.md>](../../prds/opentelemetry-instrumentation.md)

## What to build

Integrate the OpenTelemetry initialization into the FastAPI application lifecycle to ensure instrumentation starts with the application.

## Step-by-step implementation plan

1.  Modify the application entry point, likely `src/main.py`.
2.  Import the `init_telemetry` function from `src/utils/telemetry.py`.
3.  Use the FastAPI `lifespan` context manager or a `startup` event handler to call `init_teleint()`.
4.  Verify that the application starts without errors and that the telemetry initialization is triggered.

## Acceptance criteria

- [x] `init_telemetry` is called during application startup.
- [x] The application starts and remains running.
- [x] No errors are logged during the startup sequence related to telemetry.

## Blocked by

- Blocked by [03-instrumentation-setup.md](./03-instrumentation-setup.md)

## User stories addressed

- User story 1
- User story 2
- User story 3

## Implementation Details

- Modified `src/main.py` to import `init_telemetry` from `utils.telemetry`.
- Called `init_telemetry(_app)` inside the `lifespan` context manager.
- Verified that the application starts up successfully and initializes telemetry without errors.

