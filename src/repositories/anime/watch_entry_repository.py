from sqlalchemy import func as sql_func
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.anime import Anime, AnimeSeason, WatchEntry, WatchStatus


class WatchEntryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[WatchEntry]:
        return self.db.scalars(select(WatchEntry)).all()

    def get_by_id(self, entry_id: int) -> WatchEntry | None:
        return self.db.get(WatchEntry, entry_id)

    def get_watching(self) -> list[WatchEntry]:
        stmt = select(WatchEntry).where(WatchEntry.watch_status == WatchStatus.WATCHING)

        return self.db.scalars(stmt).all()

    def create(self, data: dict) -> WatchEntry:
        entry = WatchEntry(**data)

        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)

        return entry

    def update_progress(self, entry_id: int, episode: int) -> WatchEntry | None:
        entry = self.get_by_id(entry_id)

        if not entry:
            return None

        entry.current_episode = episode

        self.db.commit()
        self.db.refresh(entry)

        return entry

    def update_status(self, entry_id: int, status: WatchStatus) -> WatchEntry | None:
        entry = self.get_by_id(entry_id)

        if not entry:
            return None

        entry.watch_status = status

        self.db.commit()
        self.db.refresh(entry)

        return entry

    def delete(self, entry_id: int) -> bool:
        entry = self.get_by_id(entry_id)

        if not entry:
            return False

        self.db.delete(entry)
        self.db.commit()

        return True

    def get_currently_watching_dashboard(self):
        stmt = (
            select(
                Anime.title,
                AnimeSeason.season_number,
                WatchEntry.current_episode,
                WatchEntry.watch_status,
            )
            .join(
                AnimeSeason,
                WatchEntry.season_id == AnimeSeason.id,
            )
            .join(
                Anime,
                AnimeSeason.anime_id == Anime.id,
            )
            .where(WatchEntry.watch_status == WatchStatus.WATCHING)
        )

        return self.db.execute(stmt).all()

    def dashboard_stats(self):
        stmt = select(WatchEntry.watch_status, sql_func.count(WatchEntry.id)).group_by(WatchEntry.watch_status)  # pylint: disable=not-callable
        return self.db.execute(stmt).all()
