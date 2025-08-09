import pytest

from app.parser import ParseError, parse_chordpro, tokenize_line


def test_tokenize_line_extracts_chords_and_positions() -> None:
    chords, positions, lyrics = tokenize_line('[C]Amazing gr[G]ace')
    assert chords == ['C', 'G']
    assert positions == [0, 10]
    assert lyrics == 'Amazing grace'


def test_parse_chordpro_sections_and_lines() -> None:
    content = '{start_of_section: Verse}\n[C]Line 1\n{end_of_section}'
    parsed = parse_chordpro(content)
    assert len(parsed.sections) == 1
    assert parsed.sections[0].name == 'Verse'
    assert parsed.sections[0].lines[0].chords == ['C']


def test_parse_error_on_unclosed_section() -> None:
    with pytest.raises(ParseError):
        parse_chordpro('{start_of_section: A}')
