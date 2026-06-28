from opentelemetry import trace

from repositories.openweather.forecast_repository import ForecastRepository

tracer = trace.get_tracer(__name__)


class ForecastService:
    def __init__(self, repo: ForecastRepository):
        self.repo = repo

    def save(self, city: str):
        with tracer.start_as_current_span("forecast_service.save") as span:
            span.set_attribute("weather.city", city)
            return self.repo.run(city)
