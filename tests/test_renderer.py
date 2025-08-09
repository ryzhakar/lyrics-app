from app.parser import LineBlock, ParsedSong, Section
from app.renderer import build_chord_line, render_parsed_song


def test_build_chord_line_alignment() -> None:
    lb = LineBlock(['C', 'G'], [0, 10], 'Amazing grace')
    line = build_chord_line(lb, True)
    assert line.startswith('C')
    assert line[10] == 'G'


def test_render_parsed_song_outputs_html() -> None:
    parsed = ParsedSong([Section('Verse', [LineBlock(['C'], [0], 'Amazing')])], [])
    html = render_parsed_song(parsed, True)
    assert '<section' in html
    assert '<pre' in html
