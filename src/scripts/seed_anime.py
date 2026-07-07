import logging
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from db.database import session_local
from db.models.anime import Anime
from schemas.anime.anime import AnimeCreate
from utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class AnimeList:
    anime: list[AnimeCreate]


SEED_DATA = [
    {
        "title": "The Weakest Tamer Began a Journey to Pick Up Trash",
        "alternative_title": "Saijaku Tamer wa Gomi Hiroi no Tabi wo Hajimemashita",
        "studio": "Studio Massket",
        "release_year": 2024,
        "status": "completed",
    },
    {
        "title": "The World's Strongest Rearguard",
        "alternative_title": "Sekai Saikyou no Kouei: Meikyuukoku no Shinjin Tansakusha;The World's Strongest Rearguard: Labyrinth Country's Novice Seeker",
        "studio": "Maho Film",
        "release_year": 2026,
        "status": "airing",
    },
]


def save():
    logger.info("Starting anime seed process.")

    anime_list = AnimeList(anime=[AnimeCreate(**item) for item in SEED_DATA])
    session: Session = session_local()

    try:
        logger.info("Preparing %d anime records.", len(anime_list.anime))

        db_anime = [Anime(**anime.model_dump()) for anime in anime_list.anime]

        logger.info(
            "Truncating table %s.anime.",
            settings.anime.db_schema,
        )
        session.execute(text(f"TRUNCATE TABLE {settings.anime.db_schema}.anime RESTART IDENTITY CASCADE;"))

        logger.info("Inserting anime records.")
        session.add_all(db_anime)

        logger.info("Committing transaction.")
        session.commit()

        logger.info("Refreshing inserted records.")
        for anime in db_anime:
            session.refresh(anime)

        logger.info(
            "Successfully seeded %d anime records.",
            len(db_anime),
        )

        return db_anime

    except Exception:
        logger.exception("Failed to seed anime data. Rolling back transaction.")
        session.rollback()
        raise

    finally:
        logger.info("Closing database session.")
        session.close()


if __name__ == "__main__":
    save()
