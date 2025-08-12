from __future__ import annotations

from html import escape

from .parser import LineBlock, ParsedSong

WRAP_WIDTH = 40


def build_chord_line(line: LineBlock, show_chords: bool) -> str:
    """Build a chord line preserving positions and avoiding overlaps with spacing."""
    if not show_chords:
        return ''
    raw_tokens: list[tuple[int, str]] = []
    for idx, ch in enumerate(line.chords):
        token = ch or ''
        if not token:
            continue
        position = line.chord_positions[idx]
        raw_tokens.append((position, token))
    if not raw_tokens:
        return ''
    raw_tokens.sort(key=lambda t: t[0])
    placed: list[tuple[int, str]] = []
    last_end = -2
    for desired_start, token in raw_tokens:
        min_start = last_end + 2
        start = max(desired_start, min_start)
        placed.append((start, token))
        last_end = start + len(token) - 1
    max_len = max(start + len(tok) for start, tok in placed)
    chars: list[str] = [' '] * max_len
    for start, token in placed:
        for offset, character in enumerate(token):
            target_index = start + offset
            if target_index >= len(chars):
                chars.extend([' '] * (target_index + 1 - len(chars)))
            chars[target_index] = character
    return ''.join(chars)


def wrap_line_blocks(line: LineBlock, width: int) -> list[LineBlock]:
    """Split a line into width-bound blocks while keeping chord indices."""
    if width <= 0 or len(line.lyrics) <= width:
        return [line]
    result: list[LineBlock] = []
    start = 0
    lyrics = line.lyrics
    while start < len(lyrics):
        hard_end = min(start + width, len(lyrics))
        end = hard_end
        if end < len(lyrics):
            for i in range(end, start, -1):
                ch = lyrics[i - 1]
                if ch.isspace() or ch == '-':
                    end = i
                    break
        if end <= start:
            end = hard_end
        sub_lyrics = lyrics[start:end].rstrip()
        next_start = end
        while next_start < len(lyrics) and lyrics[next_start].isspace():
            next_start += 1
        sub_chords: list[str | None] = []
        sub_positions: list[int] = []
        for token, pos in zip(line.chords, line.chord_positions, strict=False):
            if start <= pos < next_start:
                sub_chords.append(token)
                sub_positions.append(pos - start)
        result.append(LineBlock(sub_chords, sub_positions, sub_lyrics))
        start = next_start
    return result


def render_parsed_song(parsed: ParsedSong, show_chords: bool) -> str:
    """Render a parsed song into HTML with monospace alignment."""
    parts: list[str] = []
    for section in parsed.sections:
        parts.append('<section class="song-section">')
        if section.name:
            parts.append(f'<h3 class="section-header">{escape(section.name)}</h3>')
        for line in section.lines:
            for sub in wrap_line_blocks(line, WRAP_WIDTH):
                chord_line = build_chord_line(sub, show_chords)
                lyric_line = escape(sub.lyrics)
                if chord_line:
                    parts.append('<pre class="chords">' + escape(chord_line) + '</pre>')
                parts.append('<pre class="lyrics">' + lyric_line + '</pre>')
        parts.append('</section>')
    return ''.join(parts)


def render_stream_links(youtube_url: str | None, songlink_url: str | None) -> str:
    """Render external streaming links as icon anchors."""
    links: list[str] = []
    if youtube_url:
        safe = escape(youtube_url, quote=True)
        links.append(
            '<a class="icon-link youtube" href="'
            + safe
            + '" target="_blank" rel="noopener" title="YouTube" aria-label="YouTube"></a>',
        )
    if songlink_url:
        safe = escape(songlink_url, quote=True)
        links.append(
            '<a class="icon-link spotify" href="'
            + safe
            + '" target="_blank" rel="noopener" title="Streaming" aria-label="Streaming"></a>',
        )
    return ''.join(links)
