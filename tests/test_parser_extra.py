from __future__ import annotations

import pytest

from app.parser import ParseError, parse_chordpro, strip_chordpro_to_lyrics


def test_strip_chordpro_to_lyrics_removes_markers_and_brackets() -> None:
    content = '{start_of_section: Verse}\n[C]Amazing {end_of_section}'
    text = strip_chordpro_to_lyrics(content)
    assert 'Amazing' in text
    assert '[' not in text and 'start_of_section' not in text and 'end_of_section' not in text


def test_nested_section_raises() -> None:
    content = (
        '{start_of_section: A}\n[C]Line\n{start_of_section: B}\n{end_of_section}\n{end_of_section}'
    )
    with pytest.raises(ParseError):
        parse_chordpro(content)


def test_unmatched_end_raises() -> None:
    with pytest.raises(ParseError):
        parse_chordpro('{end_of_section}')


def test_anonymous_section_parses_and_renders_without_header() -> None:
    content = '{start_of_section}\n[C]Line\n{end_of_section}'
    parsed = parse_chordpro(content)
    assert len(parsed.sections) == 1
    assert parsed.sections[0].name == ''
