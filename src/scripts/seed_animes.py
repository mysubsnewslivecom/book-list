from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import session_local
from db.models.anime import Anime, AnimeSeason

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s",
)
logger = logging.getLogger(__name__)


SEED_FILE = Path(__file__).parent.parent.parent / "data/seed_anime.json"


def load_seed_file() -> list[dict]:
    with SEED_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def seed_anime():
    anime_data = load_seed_file()

    session: Session = session_local()

    try:
        for anime_item in anime_data:
            title = anime_item["title"]

            existing = session.scalar(select(Anime).where(Anime.title == title))

            if existing:
                logger.info("Skipping existing anime: %s", title)
                continue

            anime = Anime(
                title=anime_item["title"],
                alternative_title=anime_item.get("alternative_title"),
                studio=anime_item.get("studio"),
                release_year=anime_item.get("release_year"),
                status=anime_item["status"],
            )

            for season_data in anime_item.get("seasons", []):
                season = AnimeSeason(
                    season_number=season_data["season_number"],
                    title=season_data.get("title"),
                    total_episodes=season_data.get("total_episodes"),
                )

                anime.seasons.append(season)

            session.add(anime)

            logger.info("Added: %s", title)

        session.commit()

    except Exception:
        session.rollback()
        raise


if __name__ == "__main__":
    seed_anime()
