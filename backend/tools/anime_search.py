from langchain_core.tools import Tool

from backend.vectorstore.retriever import get_retriever
from config.logging import get_logger
from config.customException import CustomException


logger = get_logger(__name__)


def _clean(value) -> str:
    """Normalize metadata values."""
    if value is None:
        return ""

    value = str(value).strip()
    if value.lower() in ("nan", "none", ""):
        return ""

    return value


def search_anime_manga(
    query: str,
    content_type: str | None = None,
    k: int = 8,
) -> str:
    """
    Search the FAISS vector store and return a formatted string.

    Args:
        query: User search query.
        content_type: "anime", "manga", or None.
        k: Number of results.

    Returns:
        Agent-friendly formatted string.
    """

    try:
        retriever = get_retriever(
            content_type=content_type,
            k=k,
        )

        docs = retriever.invoke(query)

        if not docs:
            return "No results found."

        formatted_results = []

        for doc in docs:
            metadata = doc.metadata

            title = _clean(metadata.get("title")) or "Unknown Title"

            item_type = _clean(metadata.get("content_type")).upper() or "UNKNOWN"

            score = _clean(metadata.get("score")) or "N/A"

            genres = _clean(metadata.get("genres")) or "N/A"

            status = _clean(metadata.get("status")) or "Unknown"

            synopsis = (
                doc.page_content
                or _clean(metadata.get("synopsis"))
                or "No synopsis available."
            )

            synopsis = synopsis.replace("\n", " ").strip()

            # Keep synopsis compact for agents
            if len(synopsis) > 300:
                synopsis = synopsis[:300] + "..."

            result = [
                f"[{item_type}] {title}",
                f"Score: {score} | Genres: {genres}",
                f"Status: {status}",
            ]

            if item_type == "ANIME":
                episodes = _clean(metadata.get("episodes"))

                if episodes:
                    result[-1] += f" | Episodes: {episodes}"

            elif item_type == "MANGA":
                chapters = _clean(metadata.get("chapters"))

                volumes = _clean(metadata.get("volumes"))

                extras = []

                if chapters:
                    extras.append(f"Chapters: {chapters}")

                if volumes:
                    extras.append(f"Volumes: {volumes}")

                if extras:
                    result[-1] += " | " + " | ".join(extras)

            result.append(f"Synopsis: {synopsis}")

            formatted_results.append("\n".join(result))

        return "\n---\n".join(formatted_results)

    except Exception as e:
        logger.error("Anime search tool failed: %s", e)

        raise CustomException("Failed to search anime/manga.", e)


def get_anime_search_tool(
    content_type: str | None = None,
) -> Tool:
    """
    Create a LangChain Tool wrapping FAISS search.
    """

    scope = content_type if content_type else "anime and manga"

    return Tool(
        name="anime_search",
        description=(
            f"Search the {scope} recommendation "
            "database to retrieve relevant titles. "
            "Use this tool when you need concrete "
            "anime or manga candidates, metadata, "
            "or supporting evidence before making "
            "recommendations. Input should be a "
            "natural language search query."
        ),
        func=lambda query: search_anime_manga(
            query=query,
            content_type=content_type,
        ),
    )
