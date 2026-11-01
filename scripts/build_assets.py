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

# status: "live" (public repo), "wip" (in progress, public) or "private" (private repo: not linked).
# glyph: a small schematic drawn top-right of the card (see GLYPHS below).
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
        "metric": "~80% decided locally · ~3 ms vs ~120 ms (sim)",
        "chips": ["Python", "NumPy", "Edge AI", "IEEE paper"],
        "status": "live",
        "glyph": ("tiers",),
    },
    {
        "file": "card-fogai-journal.svg",
        "tag": "NODE 02 · RESEARCH ARCHIVE",
        "repo": "/fogai-journal-v2",
        "title": "FogAI Journal",
        "lines": [
            "Pre-registered, sealed-holdout evaluation of",
            "learned fog/cloud task placement. Journal",
            "extension of the paper; manuscript in preparation.",
        ],
        "metric": "pre-registered · one-look holdout · simulation",
        "chips": ["Python", "scikit-learn", "NumPy", "SciPy"],
        "status": "private",
        "glyph": ("chain", 4),
    },
    {
        "file": "card-research-agent.svg",
        "tag": "NODE 03 · LLM SYSTEMS",
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
        "glyph": ("chain", 5),
    },
    {
        "file": "card-sree-saaj-devops.svg",
        "tag": "NODE 04 · DEVOPS",
        "repo": "/sree-saaj-devops-",
        "title": "Sree Saaj DevOps",
        "lines": [
            "Microservices platform for an events business:",
            "a JWT gateway and six FastAPI services, with",
            "Terraform, CI to ACR and Kubernetes on Azure.",
        ],
        "metric": "Terraform AKS · K8s manifests · Prometheus",
        "chips": ["Docker", "Terraform", "Kubernetes", "Ansible", "Azure"],
        "status": "live",
        "glyph": ("chain", 4),
    },
    {
        "file": "card-saaj-garage.svg",
        "tag": "NODE 05 · PRODUCT",
        "repo": "/saaj-garage",
        "title": "SAAJ Garage",
        "lines": [
            "Fleet manager for a family transport business:",
            "vehicles, document-expiry reminders, service",
            "and expense history, with private file storage.",
        ],
        "metric": "expiry reminders at 30 / 15 / 7 / 1 days",
        "chips": ["React", "TypeScript", "Supabase", "Tailwind"],
        "status": "private",
        "glyph": ("runway",),
    },
    {
        "file": "card-saaj.svg",
        "tag": "NODE 06 · PRODUCT",
        "repo": "/saaj",
        "title": "Saaj",
        "lines": [
            "Mobile-first quotation maker for an events and",
            "catering business. Builds a multi-page A4 PDF",
            "on the device; nothing is uploaded.",
        ],
        "metric": "297-dish Kerala catalogue · no backend",
        "chips": ["React", "TypeScript", "react-pdf", "Vite"],
        "status": "private",
        "glyph": ("pages",),
    },
    {
        "file": "card-java-wipro.svg",
        "tag": "NODE 07 · FUNDAMENTALS",
        "repo": "/JavaFullStack-WIPRO",
        "title": "JavaFullStack-WIPRO",
        "lines": [
            "Java exercises by experiment: console programs",
            "(arrays, strings, sorting) and a command-line",
            "employee-salary mini project.",
        ],
        "metric": "2 experiments · 7 programs · core Java only",
        "chips": ["Java 16", "Eclipse"],
        "status": "wip",
        "glyph": ("chain", 3, True),
    },
    {
        "file": "card-evora.svg",
        "tag": "NODE 08 · VISION",
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
        "glyph": ("frames",),
    },
    {
        "file": "card-parallax.svg",
        "tag": "NODE 09 · MEDICAL AI",
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
        "glyph": ("checks", 4),
    },
]

CARD_W, CARD_H, PAD = 400, 224, 24
MARGIN = 5  # transparent gutter so stacked cards never touch
CHIP_FONT = 10.5
CHIP_ADV = CHIP_FONT * 0.6


# ── card glyphs: small schematics, top-right of each card ────────────────────
# Drawn in a box x 250..376, y 46..86 (clear of the title and the top-right label).

def _chain(n: int, last_hollow: bool = False) -> str:
    xs = [258 + i * (110 / (n - 1)) for i in range(n)]
    out = [f'<path d="M{xs[0]:.1f} 66H{xs[-1]:.1f}" stroke="{CYAN}" stroke-opacity=".35" stroke-width="1.5"/>']
    for i, x in enumerate(xs):
        last = i == n - 1
        if last and last_hollow:
            out.append(f'<circle cx="{x:.1f}" cy="66" r="4.5" fill="{BG}" stroke="{DIM}" stroke-dasharray="2 2"/>')
        elif last:
            out.append(f'<circle cx="{x:.1f}" cy="66" r="5" fill="{CYAN}"/>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="66" r="4.5" fill="{BG}" stroke="{CYAN}" stroke-width="1.5"/>')
    return "".join(out)


def _tiers() -> str:
    out = []
    for y in (56, 66, 76):
        out.append(f'<circle cx="258" cy="{y}" r="2.5" fill="{CYAN}" fill-opacity=".6"/>'
                   f'<path d="M261 {y}L298 66" stroke="{CYAN}" stroke-opacity=".35"/>')
    out.append(f'<rect x="298" y="55" width="24" height="22" rx="5" fill="#0c1117" stroke="{CYAN}" stroke-width="1.5"/>')
    out.append(f'<path d="M322 62L350 54" stroke="{DIM}" stroke-dasharray="2 3"/><circle cx="358" cy="53" r="4.5" fill="{BG}" stroke="{DIM}"/>')
    out.append(f'<path d="M322 70L350 78" stroke="{CYAN}" stroke-width="1.5"/><circle cx="358" cy="79" r="4.5" fill="{CYAN}"/>')
    return "".join(out)


def _runway() -> str:
    out = [f'<path d="M258 66H362" stroke="{CYAN}" stroke-opacity=".3" stroke-width="1.5"/>']
    for x, o in ((262, .35), (292, .55), (322, .8)):
        out.append(f'<circle cx="{x}" cy="66" r="4" fill="{BG}" stroke="{CYAN}" stroke-opacity="{o}" stroke-width="1.5"/>')
    out.append(f'<circle cx="364" cy="66" r="9" fill="none" stroke="{CYAN}" stroke-opacity=".3"/><circle cx="364" cy="66" r="5.5" fill="{CYAN}"/>')
    return "".join(out)


def _pages() -> str:
    out = []
    for i in range(5):
        x = 258 + i * 24
        extra = f'<rect x="{x + 4}" y="51" width="16" height="22" rx="2.5" fill="{BG}" stroke="{CYAN}" stroke-opacity=".35"/>' if i == 1 else ""
        out.append(extra + f'<rect x="{x}" y="55" width="16" height="22" rx="2.5" fill="#0c1117" stroke="{CYAN}" stroke-opacity=".85"/>'
                   f'<path d="M{x + 3} 61H{x + 13}M{x + 3} 66H{x + 11}" stroke="{CYAN}" stroke-opacity=".45"/>')
    return "".join(out)


def _frames() -> str:
    out = []
    for i in range(3):
        x = 258 + i * 40
        out.append(f'<rect x="{x}" y="56" width="28" height="20" rx="3" fill="#0c1117" stroke="{CYAN}" stroke-opacity=".7" stroke-width="1.3"/>')
        if i < 2:
            out.append(f'<path d="M{x + 30} 66H{x + 38}" stroke="{DIM}"/>')
    out.append(f'<circle cx="312" cy="66" r="4" fill="none" stroke="{CYAN}" stroke-width="1.5"/>')
    return "".join(out)


def _checks(n: int) -> str:
    xs = [258 + i * (104 / (n - 1)) for i in range(n)]
    out = [f'<path d="M{xs[0] + 6:.1f} 66H{xs[-1]:.1f}" stroke="{CYAN}" stroke-opacity=".35" stroke-width="1.5"/>']
    for i, x in enumerate(xs):
        last = i == n - 1
        out.append(f'<rect x="{x - 7:.1f}" y="59" width="14" height="14" rx="3.5" fill="{CYAN if last else "#0c1117"}" stroke="{CYAN}" stroke-width="1.4"/>'
                   f'<path d="M{x - 3.5:.1f} 66.3l2.5 2.6 4.5-5.2" fill="none" stroke="{BG if last else CYAN}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)


def build_glyph(spec: tuple) -> str:
    kind, *args = spec
    return {"chain": _chain, "tiers": _tiers, "runway": _runway, "pages": _pages, "frames": _frames, "checks": _checks}[kind](*args)


def build_card(c: dict) -> str:
    led = AMBER if c["status"] == "wip" else CYAN
    state = "IN PROGRESS" if c["status"] == "wip" else ""
    private = c["status"] == "private"

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
    tsize = 22 if len(c["title"]) <= 17 else 20
    if PAD + len(c["title"]) * tsize * 0.58 > 252:
        raise ValueError(f"{c['file']}: title runs into the glyph")
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
    if private:
        alt = f"{c['title']} (private repository, not publicly accessible) — " + alt.split(" — ", 1)[1]
    if private:
        state_txt = (f'<text x="{CARD_W - PAD}" y="32" font-size="10.5" fill="{MUTED}" text-anchor="end" '
                     f'letter-spacing=".14em" class="m">PRIVATE</text>'
                     f'<rect x="{CARD_W - PAD - 70}" y="25.5" width="9" height="7" rx="1.5" fill="{MUTED}"/>'
                     f'<path d="M{CARD_W - PAD - 68} 25.5v-2.5a2.5 2.5 0 0 1 5 0v2.5" fill="none" stroke="{MUTED}" stroke-width="1.3"/>')
    elif state:
        state_txt = (f'<text x="{CARD_W - PAD}" y="32" font-size="10.5" fill="{AMBER}" text-anchor="end" '
                     f'letter-spacing=".14em" class="m">{state}</text>')
    else:
        state_txt = (f'<text x="{CARD_W - PAD}" y="32" font-size="11" fill="{DIM}" text-anchor="end" class="m">'
                     f'{escape(c["repo"])}</text>')
    glyph = build_glyph(c["glyph"])

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
  <text x="{PAD}" y="70" font-size="{tsize}" font-weight="600" fill="{TEXT}" class="s">{escape(c["title"])}</text>
  {glyph}
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
