from __future__ import annotations

import re
from pathlib import Path
from html import escape

from app.parser import parse_chordpro
from app.renderer import build_chord_line, render_parsed_song


def _extract_chords_before_lyrics(html: str, lyrics_text: str) -> str | None:
    pattern = re.compile(
        r'<pre class="chords">(?P<chords>.*?)</pre>\s*<pre class="lyrics">'
        + re.escape(lyrics_text)
        + r'</pre>',
        re.DOTALL,
    )
    m = pattern.search(html)
    return m.group('chords') if m else None


def test_full_render_reflects_sections_and_chords_positions() -> None:
    text = Path('example.chordpro').read_text(encoding='utf-8')
    parsed = parse_chordpro(text)
    html = render_parsed_song(parsed, show_chords=True)

    # Section headers present
    for name in ['Куплет 1', 'Приспів', 'Break', 'Заспів', 'Інтерлюдія', 'Міст 1', 'Міст 2']:
        assert f'<h3 class="section-header">{name}</h3>' in html

    # Verify a specific lyric line and chord positions in first Приспів by exact HTML block match
    pryspiv = next(s for s in parsed.sections if s.name.strip().startswith('Приспів'))
    lb = pryspiv.lines[0]
    expected_chords = build_chord_line(lb, True)
    pattern = re.compile(
        rf'<pre class="chords">{re.escape(escape(expected_chords))}</pre>'
        rf'\s*<pre class="lyrics">{re.escape(escape(lb.lyrics))}</pre>',
        re.DOTALL,
    )
    assert pattern.search(html)

    # Slash chord appears somewhere (e.g., B/F#)
    assert 'B/F#' in html

    # Parenthetical pause is a lyrics-only line (no chords before it)
    pauza = '<pre class="lyrics">(Пауза)</pre>'
    idx = html.find(pauza)
    assert idx != -1
    before = html[max(0, idx - 64) : idx]
    assert '<pre class="chords">' not in before
