import pandas as pd
from pathlib import Path
from config.settings import settings
from config.logging import get_logger
from config.customException import CustomException

logger = get_logger(__name__)


class AnimeDataLoader:
    REQUIRED_COLS = {
        "mal_id", "title", "synopsis", "genres",
        "themes", "demographics", "type", "score",
        "rank", "popularity", "status", "image_url",
        "episodes", "season", "year", "studios",
        "rating", "source",
    }

    def load_and_process(self) -> pd.DataFrame:
        try:
            logger.info("Loading anime dataset from %s", settings.data_raw_path / "anime_dataset.csv")

            df = pd.read_csv(
                settings.data_raw_path / "anime_dataset.csv",
                encoding="utf-8",
                on_bad_lines="skip",
            )

            missing = self.REQUIRED_COLS - set(df.columns)
            if missing:
                raise ValueError(f"Missing columns in anime dataset: {missing}")

            df["content_type"] = "anime"
            df["synopsis"] = df["synopsis"].fillna("")
            df["score"] = df["score"].fillna(0)
            df["genres"] = df["genres"].fillna("").str.replace("|", ", ", regex=False)
            df["themes"] = df["themes"].fillna("").str.replace("|", ", ", regex=False)
            df["demographics"] = df["demographics"].fillna("")

            before = len(df)
            df = df[(df["synopsis"].str.strip() != "") | (df["score"] >= 5.0)]
            logger.info("Quality filter: %d → %d rows", before, len(df))

            df["embed_text"] = df.apply(self._build_embed_text, axis=1)

            logger.info("Anime dataset loaded: %d rows", len(df))
            return df

        except Exception as e:
            raise CustomException("Failed to load anime dataset", e)

    @staticmethod
    def _build_embed_text(row: pd.Series) -> str:
        synopsis = row["synopsis"].strip()
        if not synopsis:
            synopsis = f"{row['title']}. {row['genres']}. {row['themes']}".strip()

        return (
            f"Title: {row['title']}\n"
            f"Type: anime | Genres: {row['genres']} | "
            f"Themes: {row['themes']} | Demographics: {row['demographics']}\n"
            f"{synopsis}"
        ).strip()


class MangaDataLoader:
    REQUIRED_COLS = {
        "mal_id", "title", "synopsis", "genres",
        "themes", "demographics", "type", "score",
        "rank", "popularity", "status", "image_url",
        "chapters", "volumes", "authors", "serializations",
    }

    def load_and_process(self) -> pd.DataFrame:
        try:
            logger.info("Loading manga dataset from %s", settings.data_raw_path / "manga_dataset.csv")
            df = pd.read_csv(
                settings.data_raw_path / "manga_dataset.csv",
                encoding="utf-8",
                on_bad_lines="skip",
            )

            missing = self.REQUIRED_COLS - set(df.columns)
            if missing:
                raise ValueError(f"Missing columns in manga dataset: {missing}")

            df["content_type"] = "manga"
            df["synopsis"] = df["synopsis"].fillna("")
            df["score"] = df["score"].fillna(0)
            df["genres"] = df["genres"].fillna("").str.replace("|", ", ", regex=False)
            df["themes"] = df["themes"].fillna("").str.replace("|", ", ", regex=False)
            df["demographics"] = df["demographics"].fillna("")

            before = len(df)
            df = df[(df["synopsis"].str.strip() != "") | (df["score"] >= 5.0)]
            logger.info("Quality filter: %d → %d rows", before, len(df))

            df["embed_text"] = df.apply(self._build_embed_text, axis=1)
            
            logger.info("Manga dataset loaded: %d rows", len(df))
            return df

        except Exception as e:
            raise CustomException("Failed to load manga dataset", e)

    @staticmethod
    def _build_embed_text(row: pd.Series) -> str:
        synopsis = row["synopsis"].strip()
        if not synopsis:
            synopsis = f"{row['title']}. {row['genres']}. {row['themes']}".strip()

        return (
            f"Title: {row['title']}\n"
            f"Type: manga | Genres: {row['genres']} | "
            f"Themes: {row['themes']} | Demographics: {row['demographics']}\n"
            f"{synopsis}"
        ).strip()


class AnimeMangaDataLoader:
    """Combines anime and manga into a single processed DataFrame."""

    def __init__(self, processed_csv: Path):
        self.processed_csv = processed_csv
        self.anime_loader = AnimeDataLoader()
        self.manga_loader = MangaDataLoader()

    def load_and_process(self) -> Path:
        try:
            anime_df = self.anime_loader.load_and_process()
            manga_df = self.manga_loader.load_and_process()

            combined = pd.concat([anime_df, manga_df], ignore_index=True)

            keep_cols = [
                "mal_id", "title", "title_english", "content_type",
                "type", "genres", "themes", "demographics", "synopsis",
                "score", "rank", "popularity", "status", "image_url",
                "embed_text",
                # anime-specific
                "episodes", "season", "year", "studios", "rating", "source",
                # manga-specific
                "chapters", "volumes", "authors", "serializations",
            ]
            combined = combined[[c for c in keep_cols if c in combined.columns]]

            self.processed_csv.parent.mkdir(parents=True, exist_ok=True)
            combined.to_csv(self.processed_csv, index=False, encoding="utf-8")

            logger.info(
                "Saved processed dataset: %d rows → %s",
                len(combined), self.processed_csv,
            )
            return self.processed_csv

        except Exception as e:
            raise CustomException("Failed to combine and save dataset", e)


if __name__ == "__main__":
    loader = AnimeMangaDataLoader(
        processed_csv=settings.data_processed_path / "combined_dataset.csv",
    )
    loader.load_and_process()