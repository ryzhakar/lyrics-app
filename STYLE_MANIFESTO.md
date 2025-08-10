## Styling Manifesto: Notes, Not Posters

### Purpose

- **Function in quiet form**: The interface exists to support reading and playing. Nothing ornamental; everything intentional.
- **Notes aesthetic**: It should feel like a calm, confident notebook—clear, stable, unbranded.
- **Mobile first**: Built for small screens, variable light, and one‑hand, quick‑glance use.

## First Principles (Dieter Rams, applied)

- **Useful**: Every element serves reading or orientation during performance.
- **Understandable**: Hierarchy is obvious; interactions are self‑evident.
- **Unobtrusive**: UI recedes; content leads. Remove when in doubt.
- **Honest**: Typography and spacing do the work; no decorative effects.
- **Long‑lasting**: Neutral palette, restrained motion, enduring rhythm.
- **As little design as possible**: Fewer styles, more clarity.

## Visual Hierarchy

- **Primary: Lyrics**—set the rhythm for everything else.
- **Secondary: Chords**—equally necessary, visually distinct, never louder than lyrics.
- **Tertiary: Sections**—service labels that structure flow without drawing focus.
- **Quaternary: Meta/Controls**—always present, nearly invisible, instantly findable.

## Typography

- **Faces**:
  - Lyrics: a calm text face with sturdy forms and even rhythm.
  - Chords: a monospace strictly for alignment, not styled as code.
  - UI: platform system font that disappears into the OS.
- **Small‑size reliability**: Prefer a slab serif (e.g., Roboto Slab) for micro text and small UI where unwavering legibility matters.
- **Scale**: Lyrics hold the largest continuous size, yet stay compact; clarity comes from spacing and contrast, not sheer size.
- **Measure**: Keep lyric line length comfortable for mobile; avoid full‑bleed lines that force horizontal scanning.
- **Rhythm**: Establish a baseline grid; chords/lyrics blocks snap to it. Spacing breathes, never crowds.

## Color and Contrast

- **Palette**: Paper and ink neutrals; one subtle accent reserved for meaning.
- **Lyrics**: Highest readable contrast.
- **Chords**: Distinct tone (weight or luminance) for instant parsing, quieter than lyrics.
- **Sections**: Lighter neutral, slight case/letter‑spacing shift to read as system information.
- **Surfaces**: Flat. Use space and alignment before lines or boxes; hairlines only when necessary.

## Layout and Spacing

- **Grid**: A simple, consistent grid underpinning all blocks; avoid deep nesting and heavy containers.
- **Breathing room**: Space is the primary design device; margins separate dense content.
- **Edge respect**: Respect safe areas and thumb zones; no important text pinned to edges.
- **Scroll**: Section‑based flow should feel like turning a page.

## Chords × Lyrics Interplay

- **Two‑line unit**: Chords above, lyrics below—locked as one read unit.
- **Alignment**: Chords align precisely over their lyric positions; no wobble.
- **Tone over theatrics**: Differentiate via tone and weight, not decoration; never use code‑like treatments.
- **Stability under transposition**: Transposing must preserve reading rhythm; spacing changes only as needed by label width.

## Sections

- **Service headers**: Quiet labels that separate content at a glance; use spacing and modest weight/size changes.
- **Separation**: Prefer white space; use hairlines sparingly for long scrolls.
- **Oversize handling**: Break long sections at natural pauses first, then at consistent intervals.

## Song Meta and Controls

- **Invisible bar**: All song meta (title, artist, key, toggles) lives in one compact, invisible bar.
- **Sticky queue**: In setlists, the meta bar is sticky; the current section name joins the sticky queue without outranking the song label.
- **Compression**: Meta compresses gracefully under scroll and never occludes lyrics.
- **Discoverability**: Always locatable within a beat; never attention‑seeking.

## Setlists

- **Continuity**: Each song reads as a chapter. A minimal divider and a meta reset create clear transitions.
- **Order clarity**: The current song is subtly emphasized; navigation chrome stays minimal.
- **Shareable state**: Visual state mirrors the URL while avoiding clutter.

## Motion and Feedback

- **Utility only**: Motion aids reading and orientation or it doesn’t exist. Respect reduced‑motion preferences.
- **Snap**: Use proximity‑based scroll snapping that feels natural; headers pin softly, without jolt.
- **Touch and focus**: Focus rings and hit feedback are clear and tasteful, never theatrical.

## Dark Mode and Environments

- **Considered inversion**: Paper‑on‑slate, not neon on black; maintain hierarchy via luminance, not saturation.
- **Low‑light reliability**: Ensure chord/lyric distinction survives dim conditions; avoid hues that merge at low brightness.
- **Ambient resilience**: Do not rely on delicate color differences likely to wash out in bright light.

## Accessibility and Performance Use

- **Contrast discipline**: Maintain accessible contrast for all text across modes.
- **Size discipline**: Preserve hierarchy; use spacing and rhythm before scaling up type.
- **Glance latency**: The layout must be instantly re‑parsable after every glance away from the screen.

## What to Avoid

- Heavy backgrounds, gradients, textures, frosted glass.
- Code‑like chord treatments, boxes and pills around text, tinted code blocks.
- Overscaled lyrics, shouting section headers, decorative dividers.
- Excess icons; prefer plain language or nothing.

## Implementation Posture (Non‑Prescriptive)

- Use a minimal token set (paper/ink neutrals, single accent) and a baseline grid to govern decisions.
- Treat monospace chords as text peers: same baseline, calibrated tone/weight; never styled as code.
- Keep all meta in one compact bar; metadata never spills into the content stream.
- Encode hierarchy with tone, spacing, and weight before size or decoration.

## Return to the Spirit

- **Calm confidence**: A tool that disappears into use—quiet, precise, unyieldingly readable.
- **Music first**: The eye moves like a metronome. Typography sets tempo; spacing keeps time.
- **As little design as possible**: Every pixel earns its keep; simplicity wins when choices are equal.
- **Enduring utility**: Built to be played with. When noticed, it feels inevitable.
