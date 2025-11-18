"""Tests for metadata extraction and lyric sanitization feeding the search UI."""

from __future__ import annotations

import re
import sys
from pathlib import Path
import textwrap

import pytest

# Ensure the src package is importable when tests run directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from genlist_butler.cli import (  # pylint: disable=wrong-import-position
    _sanitize_lyric_text,
    extract_chopro_metadata,
    main as cli_main,
)


@pytest.mark.parametrize(
    "line,expected",
    [
        ("merri[D7]ly", "merrily"),
        ("Ev'ryone [D7]dancing [Am7]merri-[D7]ly", "Ev'ryone dancing merrily"),
        ("Love, the [C]guest, is [D] on the [G] way.", "Love, the guest, is on the way."),
        ("People look [D7] east and sing to-[G]-day", "People look east and sing today"),
    ],
)
def test_sanitize_lyric_text_strips_chords_and_hyphens(line: str, expected: str) -> None:
    """Inline chords and syllable hyphenation artifacts should disappear for search."""

    assert _sanitize_lyric_text(line) == expected


def test_extract_chopro_metadata_collects_tokens(tmp_path: Path) -> None:
    """ChordPro metadata parsing should surface keywords, titles, subtitles, and lyrics."""

    song_text = textwrap.dedent(
        """
        {title: Rockin' Around}
        {subtitle: Holiday Classic}
        {keywords: festive; party time}

        Ev'ryone [D7]dancing [Am7]merri-[D7]ly, in the new old-[D7]fashioned way.
        People look [D7] east and sing to-[G]-day.
        """
    ).strip()

    song_path = tmp_path / "sample.chopro"
    song_path.write_text(song_text, encoding="utf-8")

    metadata = extract_chopro_metadata(str(song_path))

    assert metadata["titles"] == {"Rockin' Around"}
    assert metadata["subtitles"] == {"Holiday Classic"}
    assert metadata["keywords"] == {"festive", "party time"}
    assert metadata["lyrics"] == [
        "Ev'ryone dancing merrily, in the new old fashioned way.",
        "People look east and sing today.",
    ]


def test_cli_embeds_metadata_attributes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """End-to-end run should emit data- attributes populated with metadata and lyrics."""

    music_dir = tmp_path / "music"
    music_dir.mkdir()

    chart_contents = textwrap.dedent(
        """
        {title: People Look East}
        {subtitle: Advent Hymn}
        {keywords: liturgy; flourish}

        People look [D7] east and sing to-[G]-day.
        Flour-[Am]ish with [Em]hope to[G]-day.
        """
    ).strip()

    chart_path = music_dir / "People Look East.chopro"
    chart_path.write_text(chart_contents, encoding="utf-8")

    output_file = tmp_path / "catalog.html"

    argv = [
        "genlist",
        str(music_dir),
        str(output_file),
        "--no-intro",
        "--no-line-numbers",
        "--filter",
        "none",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    # Run the CLI to generate HTML with embedded search metadata
    cli_main()

    html_output = output_file.read_text(encoding="utf-8")

    metadata_attr = re.search(r'data-metadata="([^"]*)"', html_output)
    assert metadata_attr, "data-metadata attribute missing"
    metadata_tokens = metadata_attr.group(1).split()
    assert set(metadata_tokens) == {"advent", "hymn", "flourish", "liturgy", "people", "look", "east"}

    lyrics_attr = re.search(r'data-lyrics="([^"]*)"', html_output)
    assert lyrics_attr, "data-lyrics attribute missing"
    lyrics_value = lyrics_attr.group(1).lower()
    normalized_lyrics = re.sub(r"[^\w\s']", " ", lyrics_value)
    assert "people look east and sing today" in normalized_lyrics
    assert "flourish with hope today" in normalized_lyrics

    assert "People Look East" in html_output
