from __future__ import annotations

from app.parser import LineBlock, ParsedSong, Section
from app.renderer import build_chord_line
from app.renderer import render_parsed_song


def test_build_chord_line_preserves_anchor_columns() -> None:
    lb = LineBlock(['Am7', 'Fmaj7'], [0, 10], 'lyrics')
    line = build_chord_line(lb, True)
    assert line.startswith('Am7')
    assert line[10] == 'F'


def test_build_chord_line_hidden_when_flag_false() -> None:
    lb = LineBlock(['C'], [0], 'lyrics')
    assert build_chord_line(lb, False) == ''


def test_render_parsed_song_escapes_html() -> None:
    section = Section('<Verse>', [LineBlock(['C'], [0], '<b>text</b>')])
    html = render_parsed_song(ParsedSong([section], []), True)
    assert '&lt;Verse&gt;' in html
    assert '&lt;b&gt;text&lt;/b&gt;' in html


def test_build_chord_line_resolves_overlaps_with_spacing() -> None:
    lb = LineBlock(['Ebm', 'Ab/Eb', 'Bb/Eb'], [4, 8, 12], 'О — о — о')
    line = build_chord_line(lb, True)
    assert 'Ebm' in line
    assert 'Ab/Eb' in line
    assert 'Bb/Eb' in line
    first = line.index('Ebm')
    second = line.index('Ab/Eb')
    third = line.index('Bb/Eb')
    assert second >= first + len('Ebm') + 1
    assert third >= second + len('Ab/Eb') + 1
