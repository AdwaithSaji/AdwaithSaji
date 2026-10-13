"""Generate the typing strip and project cards in assets/.

Edit PHRASES or CARDS below, then run:  python scripts/build_assets.py
Stdlib only. Output is deterministic, so regenerated files diff cleanly.
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SANS = "'Inter', 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', 'Cascadia Code', Consolas, 'Liberation Mono', Menlo, monospace"

BG = "#07090c"
EDGE = "#1a222d"
TEXT = "#e8edf2"
MUTED = "#8b97a5"
DIM = "#5b6878"
CYAN = "#3fe0ee"
AMBER = "#f2b45a"

# ── typing strip ───────────────────────────────────────────────────────────

PHRASES = [
    "edge AI for industrial IoT",
    "medical AI that proves its findings",
    "LLM agents that cite their sources",
    "search across camera streams in plain English",
    "Spring Boot and FastAPI backends",
    "cloud infrastructure as code",
]

TYPE_FONT = 20
ADVANCE = TYPE_FONT * 0.6  # monospace advance; textLength pins every font to it
CHAR_TIME = 0.055          # seconds per typed character
HOLD = 2.6                 # seconds a finished phrase stays on screen
DELETE = 0.5               # seconds to erase a phrase
GAP = 0.35                 # blank time before the next phrase


def build_typing() -> str:
    w, h = 1200, 64
    x0 = 172
    slots = [len(p) * CHAR_TIME + HOLD + DELETE + GAP for p in PHRASES]
    total = sum(slots)

    def pct(t: float) -> str:
        return f"{100 * t / total:.3f}%"

    css, groups = [], []
    start = 0.0
    for i, phrase in enumerate(PHRASES):
        n = len(phrase)
        width = n * ADVANCE
        typed = start + n * CHAR_TIME
        held = typed + HOLD
        erased = held + DELETE
        hidden = start + slots[i]
        eps = 0.001

        # Visibility: on only during this phrase's slot.
        if i == 0:
            vis = f"0%{{opacity:1}} {pct(hidden - eps)}{{opacity:1}} {pct(hidden)}{{opacity:0}} 100%{{opacity:0}}"
        else:
            vis = (f"0%{{opacity:0}} {pct(start - eps)}{{opacity:0}} {pct(start)}{{opacity:1}} "
                   f"{pct(hidden - eps)}{{opacity:1}} {pct(hidden)}{{opacity:0}} 100%{{opacity:0}}")
        # Cover slides right one character per step, holds, then steps back.
        move = (f"0%{{transform:translateX(0)}} "
                f"{pct(start)}{{transform:translateX(0);animation-timing-function:steps({n},end)}} "
                f"{pct(typed)}{{transform:translateX({width:.1f}px);animation-timing-function:linear}} "
                f"{pct(held)}{{transform:translateX({width:.1f}px);animation-timing-function:steps({n},end)}} "
                f"{pct(erased)}{{transform:translateX(0)}} 100%{{transform:translateX(0)}}")
        default_vis = 1 if i == 0 else 0
        css.append(f"@keyframes v{i}{{{vis}}} @keyframes m{i}{{{move}}}")
        css.append(f".p{i}{{opacity:{default_vis};animation:v{i} {total:.2f}s infinite both}}"
                   f".c{i}{{transform:translateX({width:.1f}px);animation:m{i} {total:.2f}s infinite both}}")
        groups.append(
            f'<g class="p{i}">'
            f'<text x="{x0}" y="40" font-size="{TYPE_FONT}" fill="{TEXT}" textLength="{width:.1f}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{escape(phrase)}</text>'
            f'<g class="c{i}"><rect x="{x0}" y="14" width="{w}" height="38" fill="{BG}"/>'
            f'<rect class="cur" x="{x0 + 2}" y="22" width="10" height="24" fill="{CYAN}"/></g></g>'
        )
        start = hidden

    reduced = "".join(f".p{i},.c{i}" + ("," if i < len(PHRASES) - 1 else "") for i in range(len(PHRASES)))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t">
  <title id="t">Interests: {escape("; ".join(PHRASES))}</title>
  <style>
    text {{ font-family: {MONO}; }}
    .cur {{ animation: blink 1s steps(1, end) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    {" ".join(css)}
    @media (prefers-reduced-motion: reduce) {{ {reduced} {{ animation: none; }} .cur {{ animation: none; }} }}
  </style>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{BG}" stroke="{EDGE}"/>
  <text x="40" y="38" font-size="12" fill="{DIM}" letter-spacing=".2em">FOCUS</text>
  <text x="148" y="39" font-size="{TYPE_FONT}" fill="{CYAN}">&gt;</text>
  {"".join(groups)}
</svg>
"""


# ── project cards ──────────────────────────────────────────────────────────

CARDS = [
    {
        "file": "card-fogai.svg",
        "tag": "NODE 01 · RESEARCH",
        "repo": "/FogAi",
        "title": "FogAI",
        "lines": [
            "Hybrid rule + risk-scoring engine that keeps",
            "safety-critical IIoT decisions on the fog node",
            "and keeps working through cloud outages.",
        ],
        "metric": "~75% decided locally · ~3 ms vs ~120 ms (sim)",
        "chips": ["Python", "NumPy", "Edge AI", "IEEE paper"],
        "status": "live",
    },
    {
        "file": "card-research-agent.svg",
        "tag": "NODE 02 · LLM SYSTEMS",
        "repo": "/ai-research-agent",
        "title": "AI Research Agent",
        "lines": [
            "Bounded plan → search → verify → synthesize",
            "pipeline. Citations are assigned in code and",
            "quotes are checked against retrieved pages.",
        ],
        "metric": "SSE progress stream · 22-question eval harness",
        "chips": ["FastAPI", "Pydantic", "React + TS", "Docker"],
        "status": "live",
    },
    {
        "file": "card-evora.svg",
        "tag": "NODE 03 · VISION",
        "repo": "/febinrenu/EVORA",
        "title": "EVORA",
        "lines": [
            "Ask plain-English questions of many cameras;",
            "get back the camera, the time and a clip with",
            "the object circled. I planned and bootstrapped it.",
        ],
        "metric": "detect → track → re-id → retrieve → answer",
        "chips": ["YOLOE", "ByteTrack", "SigLIP", "OSNet", "Ollama"],
        "status": "live",
    },
    {
        "file": "card-parallax.svg",
        "tag": "NODE 04 · MEDICAL AI",
        "repo": "/febinrenu/PARALLAX",
        "title": "Parallax",
        "lines": [
            "Multimodal medical second opinion: every finding",
            "must survive a chain of checks before a doctor",
            "sees it. My part: OOD routing and verification.",
        ],
        "metric": "deletion test · 8-way stability · MedSAM masks",
        "chips": ["PyTorch", "FastAPI", "MedSAM", "MedGemma"],
        "status": "live",
    },
]

CARD_W, CARD_H, PAD = 400, 224, 24
MARGIN = 5  # transparent gutter so stacked cards never touch
CHIP_FONT = 10.5
CHIP_ADV = CHIP_FONT * 0.6


def build_card(c: dict) -> str:
    led = AMBER if c["status"] == "wip" else CYAN
    state = "IN PROGRESS" if c["status"] == "wip" else ""

    chips, x = [], PAD
    for label in c["chips"]:
        tw = len(label) * CHIP_ADV
        cw = tw + 16
        chips.append(
            f'<rect x="{x}" y="186" width="{cw:.1f}" height="20" rx="4" fill="#0c1117" stroke="#222c38"/>'
            f'<text x="{x + 8}" y="200" font-size="{CHIP_FONT}" fill="{MUTED}" textLength="{tw:.1f}" '
            f'lengthAdjust="spacingAndGlyphs" class="m">{escape(label)}</text>'
        )
        x += cw + 6
    if x - 6 > CARD_W - PAD:
        raise ValueError(f"{c['file']}: chips overflow by {x - 6 - (CARD_W - PAD):.0f}px")
    for line in c["lines"]:
        if len(line) > 50:
            raise ValueError(f"{c['file']}: line too long ({len(line)} chars): {line}")
    if len(c["metric"]) * 11.5 * 0.6 > CARD_W - 2 * PAD:
        raise ValueError(f"{c['file']}: metric too long")

    body = "".join(
        f'<text x="{PAD}" y="{98 + 20 * i}" font-size="13.5" fill="{MUTED}" class="s">{escape(t)}</text>'
        for i, t in enumerate(c["lines"])
    )
    alt = f"{c['title']} — {' '.join(c['lines'])} {c['metric']}. Stack: {', '.join(c['chips'])}."
    if state:
        alt = f"{c['title']} (in progress) — " + alt.split(" — ", 1)[1]
    state_txt = (f'<text x="{CARD_W - PAD}" y="32" font-size="10.5" fill="{AMBER}" text-anchor="end" '
                 f'letter-spacing=".14em" class="m">{state}</text>') if state else (
                 f'<text x="{CARD_W - PAD}" y="32" font-size="11" fill="{DIM}" text-anchor="end" class="m">'
                 f'{escape(c["repo"])}</text>')

    ow, oh = CARD_W + 2 * MARGIN, CARD_H + 2 * MARGIN
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-MARGIN} {-MARGIN} {ow} {oh}" width="{ow}" height="{oh}" role="img" aria-labelledby="t">
  <title id="t">{escape(alt)}</title>
  <style>
    .s {{ font-family: {SANS}; }}
    .m {{ font-family: {MONO}; }}
    .led {{ animation: pulse 2.8s ease-in-out infinite; }}
    @keyframes pulse {{ 50% {{ opacity: .35; }} }}
    @media (prefers-reduced-motion: reduce) {{ .led {{ animation: none; }} }}
  </style>
  <defs>
    <radialGradient id="g" cx="0" cy="0" r="1" gradientTransform="translate(28 28) scale(260 180)" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{led}" stop-opacity=".09"/><stop offset="1" stop-color="{led}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x=".5" y=".5" width="{CARD_W - 1}" height="{CARD_H - 1}" rx="12" fill="{BG}" stroke="{EDGE}"/>
  <rect x=".5" y=".5" width="{CARD_W - 1}" height="{CARD_H - 1}" rx="12" fill="url(#g)"/>
  <circle cx="{PAD + 4}" cy="28" r="7" fill="{led}" opacity=".12" class="led"/>
  <circle cx="{PAD + 4}" cy="28" r="3.5" fill="{led}"/>
  <text x="{PAD + 18}" y="32" font-size="10.5" fill="{DIM}" letter-spacing=".14em" class="m">{escape(c["tag"])}</text>
  {state_txt}
  <text x="{PAD}" y="70" font-size="22" font-weight="600" fill="{TEXT}" class="s">{escape(c["title"])}</text>
  {body}
  <text x="{PAD}" y="168" font-size="11.5" fill="{CYAN}" class="m">{escape(c["metric"])}</text>
  <path d="M{PAD} 176.5H{CARD_W - PAD}" stroke="#141b23"/>
  {"".join(chips)}
</svg>
"""


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "typing.svg").write_text(build_typing(), encoding="utf-8", newline="\n")
    for c in CARDS:
        (ASSETS / c["file"]).write_text(build_card(c), encoding="utf-8", newline="\n")
    print(f"wrote typing.svg and {len(CARDS)} cards to {ASSETS}")


if __name__ == "__main__":
    main()
