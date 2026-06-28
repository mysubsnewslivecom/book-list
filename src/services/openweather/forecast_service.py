from repositories.openweather.forecast_repository import ForecastRepository


class ForecastService:
    def __init__(self, repo: ForecastRepository):
        self.repo = repo

    def save(self, city: str):
        return self.repo.run(city)
