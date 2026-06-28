import logging
from typing import Any

from opentelemetry import trace

from repositories.anime import WatchEntryRepository

tracer = trace.get_tracer(__name__)


class WatchEntryService:
    def __init__(self, repo: WatchEntryRepository):
        self.repo = repo

    def get_all(self):
        with tracer.start_as_current_span("watch_entry_service.get_all"):
            return self.repo.get_all()

    def create(self, payload: dict[str, Any]):
        with tracer.start_as_current_span("watch_entry_service.create") as span:
            span.set_attribute("entry.title", payload.get("title"))
            return self.repo.create(data=payload)

    def update_progress(self, entry_id: int, episode: int):
        with tracer.start_as_current_span("watch_entry_service.update_progress") as span:
            span.set_attribute("watch_entry.id", entry_id)
            span.set_attribute("watch_entry.episode", episode)
            return self.repo.update_progress(entry_id=entry_id, episode=episode)

    def update_status(self, entry_id: int, watch_status: str):
        with tracer.start_as_current_span("watch_entry_service.update_status") as span:
            span.set_attribute("watch_entry.id", entry_id)
            span.set_attribute("watch_entry.status", watch_status)
            return self.repo.update_status(entry_id=entry_id, status=watch_status)

    def delete(self, entry_id: int):
        with tracer.start_as_current_span("watch_entry_service.delete") as span:
            span.set_attribute("watch_entry.id", entry_id)
            return self.repo.delete(entry_id=entry_id)

    def dashboard_stats(self):
        with tracer.start_as_current_span("watch_entry_service.dashboard_stats"):
            stats = {
                "watching": 0,
                "completed": 0,
                "on_hold": 0,
                "dropped": 0,
                "plan_to_watch": 0,
            }

            rows = self.repo.dashboard_stats()
            logging.info(rows)
            for status, count in rows:
                logging.info("Status: %s, Count: %s", status, count)
                if isinstance(status, str):
                    stats[status] = count
                    continue
                stats[status.value] = count

            return stats
