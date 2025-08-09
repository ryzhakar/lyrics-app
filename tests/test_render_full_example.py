from __future__ import annotations

import re
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
    text = """{start_of_section: Куплет 1}
[B]Тату мо[A]єму
на[E]лежить Усесвіт
і [Em6]подих оцей мій:
[G#m7]о — о — [Emaj9]о.
{end_of_section}

{start_of_section: Break}
[B][A][B]
{end_of_section}

{start_of_section: Куплет 2}
[B]Зітхав нао[A]динці
до [E]Щедрого Бога
від [Em6]серця усього:
[G#m7]о — о — [Emaj9]о.
{end_of_section}

{start_of_section: Break}
[B][A][B]
{end_of_section}

{start_of_section: Приспів}
Захов[E]аєш[F#] тут у розкоші твор[B]іння[G#m7]
над безоднею ха[E]осу[F#] мене[G#m7].        [D#m7]
Довір[E]яєш[F#] мені місце поклон[B]іння[G#m7][B/F#],
де спокійно мені [Gmaj7]досі й [Cmaj7]тепер.
{end_of_section}

{start_of_section: Break}
[B][A][B]
{end_of_section}

{start_of_section: Куплет 3}
[B]Подихом [A]легким
ход[E]ив поміж нами
хол[Em6]одними днями.
{end_of_section}

{start_of_section: Куплет 4}
[B]Нас очищ[A]ає –
тво[E]ю душу й мою –
вогн[Em6]ем і водою.
{end_of_section}

{start_of_section: Заспів}
[G#m7]О — о — [Emaj9]о,
[G#m7]о — о — [Emaj9]о,
[G#m7]о — о — [Emaj9]о.
{end_of_section}
{start_of_section: Break}
[B][A][B]
{end_of_section}

{start_of_section: Приспів}
Захов[E]аєш[F#] тут у розкоші твор[B]іння[G#m7]
над безоднею ха[E]осу[F#] мене[G#m7].        [D#m7]
Довір[E]яєш[F#] мені місце поклон[B]іння[G#m7][B/F#],
де спокійно мені [Gmaj7]досі й [Cmaj7]тепер.
{end_of_section}

{start_of_section: Break}
[B][A][B][A]
[B][A][B][A]
{end_of_section}

{start_of_section: Інтерлюдія}
О — [Em]о — [A/E]о — [B/E]о — о!
О — [Em]о — [A/E]о — [B/E]о — о!
Усе Твор[Em]іння Теб[A/E]е чека[B/E]є!
Усе Твор[Em]іння Тебе чека[Bm/D]є!
{end_of_section}

{start_of_section: Break}
(Пауза)
{end_of_section}

{start_of_section: Break}
[G#m7][Em][B]
[G#m7][Em][B]
{end_of_section}

{new_page}
{start_of_section: Міст 1}
Там на [G#m7]пагорбі в саду
промін[Em]яв на вигоду
все, що Т[B]и даєш задарма,
розгубив набуте [D#m]марно.

Квітне [G#m7]дерево в саду,
де раз[Em]ом з Тобою був.
Люди т[B]ут палили жертву:
тут на дереві помер [D#m]Ти.
{end_of_section}

{start_of_section: Міст 2}
Там на [Emaj7]пагорбі в саду
промін[F#]яв на вигоду
все, що Т[G#m7]и даєш задарма,
розгу[F#]бив набуте марно.
Квітне [Emaj7]дерево в саду,
де раз[F#]ом з Тобою був.
Люди т[G#m7]ут палили жертву:
тут на де[D#m7]реві помер Ти.
{end_of_section}

{start_of_section: Приспів}
Захов[E]аєш[F#] тут у розкоші твор[B]іння[G#m7]
над безоднею ха[E]осу[F#] мене[G#m7].        [D#m7]
Довір[E]яєш[F#] мені місце поклон[B]іння[G#m7][B/F#],
де спокійно мені [Gmaj7]досі й [Cmaj7]тепер.
{end_of_section}

{start_of_section: Break}
[B][A][B][A]
[B][A][B][A]
{end_of_section}"""
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
