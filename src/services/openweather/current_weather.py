from repositories.openweather.current_weather_repository import CurrentWeatherRepository


class CurrentWeatherService:
    def __init__(self, repo: CurrentWeatherRepository):
        self.repo = repo

    def fetch(self, city: str):
        return self.repo.fetch_if_needed(city_name=city)
