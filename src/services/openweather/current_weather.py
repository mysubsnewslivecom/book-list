from opentelemetry import trace

from repositories.openweather.current_weather_repository import CurrentWeatherRepository

tracer = trace.get_tracer(__name__)


class CurrentWeatherService:
    def __init__(self, repo: CurrentWeatherRepository):
        self.repo = repo

    def fetch(self, city: str):
        with tracer.start_as_current_span("current_weather_service.fetch") as span:
            span.set_attribute("weather.city", city)
            return self.repo.fetch_if_needed(city_name=city)
