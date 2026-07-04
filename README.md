# PolicyEngine July 4, 2026 🎆

250 years of American independence — July 4, 1776 to July 4, 2026.

## Live page

[Animated fireworks page](https://policyengine.github.io/july4-2026/) — sequel to [halloween-2025](https://github.com/PolicyEngine/halloween-2025). The real PolicyEngine wordmark (the actual SVG paths, recolored red, white, and blue) over the Federalist No. 62 quote, under a slow fireworks sky.

## Videos

- `videos/fireworks-silent.mp4` — 15 s loop, 1080p, 30 fps, silent
- `videos/fireworks-soundtrack.mp4` — same loop with a synthesized soundtrack: booms, crackles, and launch whistles timed to each burst

## Federalist No. 62 card

`assets/federalist-62-card.png` — social card for the 250th anniversary, quoting [Federalist No. 62](https://avalon.law.yale.edu/18th_century/fed62.asp) (1788):

> "It will be of little avail to the people, that the laws are made by men of their own choice, if the laws be so voluminous that they cannot be read, or so incoherent that they cannot be understood…"

Making the law computable is PolicyEngine's answer to that 238-year-old worry.

## How the video was rendered

No screen recording and no DevTools protocol — every frame is an independent headless Chrome screenshot of a deterministic simulation:

1. `index.html?record=1` seeds the PRNG (mulberry32), so every load replays the identical 15-second show.
2. `?frame=N` advances the simulation N output frames synchronously (two 60 fps ticks per 30 fps frame), then repaints on every animation frame — a late layout resize otherwise resets the canvas buffer and wipes a one-time draw.
3. `tools/render-frame.sh` renders all 450 frames as parallel `chrome --headless --screenshot` runs; ffmpeg assembles them.
4. `?frame=450&logs=1` dumps the burst/launch event log (`tools/logs.json`); `tools/soundtrack.py` synthesizes the audio from it with numpy — FFT-filtered noise booms, impulse-train crackles, whistles swept along each rocket's flight, stereo-panned to each burst's screen position.

## Colors

- Flag-inspired red `#FF4D5E` and blue `#5B8DEF` on a night-sky navy gradient
- PolicyEngine teal `#38B2AC` and gold `#FFD166` in the bursts

---

Made with PolicyEngine's commitment to evidence-based analysis — and to laws that can be read and understood.

[policyengine.org](https://policyengine.org)
