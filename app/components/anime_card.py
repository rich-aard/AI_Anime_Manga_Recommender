

from typing import Any
import streamlit as st


def _clean(value: Any) -> str:
    """Convert None / empty / NaN values into an empty string."""
    if value is None:
        return ""
    value = str(value).strip()
    if value.lower() in ("nan", "none", ""):  
        return ""
    return value


def render_anime_card(metadata: dict) -> None:
    """
    Render a single anime/manga card.

    Expected metadata keys:
        title
        content_type
        type
        genres
        themes
        score
        rank
        status
        episodes
        season
        year
        studios
        chapters
        volumes
        authors
        image_url
    """

    title = _clean(metadata.get("title")) or "Unknown Title"

    content_type = _clean(metadata.get("content_type")).lower()

    genres = _clean(metadata.get("genres"))
    themes = _clean(metadata.get("themes"))

    score = _clean(metadata.get("score"))
    status = _clean(metadata.get("status"))
    rank = _clean(metadata.get("rank"))

    episodes = _clean(metadata.get("episodes"))
    studios = _clean(metadata.get("studios"))

    chapters = _clean(metadata.get("chapters"))
    volumes = _clean(metadata.get("volumes"))
    authors = _clean(metadata.get("authors"))

    season = _clean(metadata.get("season"))
    year = _clean(metadata.get("year"))

    image_url = _clean(metadata.get("image_url"))

    badge = (
        "ANIME"
        if content_type == "anime"
        else "MANGA"
    )

    score_text = (
        f"⭐ {score}/10"
        if score
        else "⭐ Unscored"
    )

    season_year = ""

    if season and year:
        season_year = f"{season.title()} {year}"
    elif year:
        season_year = year
    elif season:
        season_year = season.title()

    with st.container(border=True):

        col_img, col_info = st.columns([1, 3])

     
        with col_img:

            if image_url:
                st.image(
                    image_url,
                    width=80,
                )
            else:
                st.markdown(
                    "<div style='font-size:60px;text-align:center;'>🎌</div>",
                    unsafe_allow_html=True,
                )

        with col_info:

            st.markdown(f"### {title}")

            header_parts = [
                badge,
                score_text,
            ]

            if rank:
                header_parts.append(f"Rank #{rank}")

            st.caption(" • ".join(header_parts))

            if genres:
                st.write(f"**Genres:** {genres}")

            if themes:
                st.write(f"**Themes:** {themes}")

            if status:
                st.write(f"**Status:** {status}")

            # Anime-specific fields
            if content_type == "anime":

                if episodes:
                    st.write(
                        f"**Episodes:** {episodes}"
                    )

                if studios:
                    st.write(
                        f"**Studios:** {studios}"
                    )

            # Manga-specific fields
            elif content_type == "manga":

                chapter_info = []

                if chapters:
                    chapter_info.append(
                        f"Chapters: {chapters}"
                    )

                if volumes:
                    chapter_info.append(
                        f"Volumes: {volumes}"
                    )

                if chapter_info:
                    st.write(
                        "**"
                        + " · ".join(chapter_info)
                        + "**"
                    )

                if authors:
                    st.write(
                        f"**Authors:** {authors}"
                    )

            if season_year:
                st.caption(season_year)


def render_source_list(
    sources: list[dict],
) -> None:
    """
    Render a list of recommendation cards.
    """

    if not sources:
        st.info("No sources retrieved.")
        return

    for i,source in enumerate(sources):

        render_anime_card(source)
        if i < len(sources) - 1:      
            st.divider()