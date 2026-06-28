import logging
from typing import Any

from repositories.anime import WatchEntryRepository


class WatchEntryService:
    def __init__(self, repo: WatchEntryRepository):
        self.repo = repo

    def get_all(self):
        return self.repo.get_all()

    def create(self, payload: dict[str, Any]):
        return self.repo.create(data=payload)

    def update_progress(self, entry_id: int, episode: int):
        return self.repo.update_progress(entry_id=entry_id, episode=episode)

    def update_status(self, entry_id: int, watch_status: str):
        return self.repo.update_status(entry_id=entry_id, status=watch_status)

    def delete(self, entry_id: int):
        return self.repo.delete(entry_id=entry_id)

    def dashboard_stats(self):
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
            logging.info(f"Status: {status}, Count: {count}")
            if isinstance(status, str):
                stats[status] = count
                continue
            stats[status.value] = count

        return stats
