"""Generate the README cover banners for the seven featured repositories.

One design system, seven isometric illustrations. The frame, grid, glow, type
hierarchy, label column and line-art style are shared with assets/header.svg;
only the illustration, copy and status change per repository.

    python scripts/build_readme_banners.py                 # write to ./banners/
    python scripts/build_readme_banners.py --out DIR       # write <slug>.svg into DIR
    python scripts/build_readme_banners.py --repos-root "C:/Github fix"
                                                           # write each repo's assets/readme/banner.svg

Stdlib only; output is deterministic.
"""
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 1200, 380

# ── design tokens (from assets/header.svg and the profile cards) ─────────────
BG, EDGE = "#07090c", "#1a222d"
TEXT, MUTED, DIM, FAINT = "#e8edf2", "#8b97a5", "#5b6878", "#4a5664"
CYAN, CYAN_DEEP = "#3fe0ee", "#2a6d75"
AMBER = "#f2b45a"
SANS = "'Inter', 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', 'Cascadia Code', Consolas, 'Liberation Mono', Menlo, monospace"

# ── isometric projection, matched to the header's flat iso plates ───────────
OX = 860          # screen x of the world origin
KX, KY = 0.866, 0.22


def P(x, y, z=0.0, oy=0.0):
    return (OX + (x - y) * KX, oy + (x + y) * KY - z)


def pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


class Art:
    """Collects SVG fragments plus label anchors for one illustration."""

    def __init__(self, oy):
        self.oy = oy
        self.parts = []
        self.anchors = []   # (order, name, sub, ax, ay)
        self.direction = "up"   # "up": 01 at the bottom (stacks), "down": 01 at the top (flows)

    def p(self, x, y, z=0.0):
        return P(x, y, z, self.oy)

    def add(self, s):
        self.parts.append(s)

    # box from (x,y,z) with size (w,d,h); the top face sits at z+h.
    def box(self, x, y, z, w, d, h, face="face", inner=0, hl=False):
        a, b, c, e = self.p(x, y, z + h), self.p(x + w, y, z + h), self.p(x + w, y + d, z + h), self.p(x, y + d, z + h)
        a0, b0, c0, e0 = self.p(x, y, z), self.p(x + w, y, z), self.p(x + w, y + d, z), self.p(x, y + d, z)
        if h > 0:
            self.add(f'<polygon points="{pts([e, c, c0, e0])}" class="side-l"/>'
                     f'<polygon points="{pts([b, c, c0, b0])}" class="side-r"/>')
        cls = "hl" if hl else face
        self.add(f'<polygon points="{pts([a, b, c, e])}" class="{cls}"/>')
        if inner:
            i = inner
            ia, ib, ic, ie = (self.p(x + i, y + i, z + h), self.p(x + w - i, y + i, z + h),
                              self.p(x + w - i, y + d - i, z + h), self.p(x + i, y + d - i, z + h))
            self.add(f'<polygon points="{pts([ia, ib, ic, ie])}" class="inner"/>')

    def line(self, p1, p2, cls="wire", dash=False):
        d = ' stroke-dasharray="2 4"' if dash else ""
        self.add(f'<path d="M{p1[0]:.1f} {p1[1]:.1f}L{p2[0]:.1f} {p2[1]:.1f}" class="{cls}"{d}/>')

    def disc(self, x, y, z, r=7, fill=False, glow=False):
        cx, cy = self.p(x, y, z)
        if glow:
            self.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * 2.2:.1f}" ry="{r * 1.1:.1f}" fill="{CYAN}" opacity=".13"/>')
        f = CYAN if fill else "#0a1317"
        self.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * 1.1:.1f}" ry="{r * .55:.1f}" fill="{f}" stroke="{CYAN}" stroke-width="1.3"/>')

    def dot(self, x, y, z, r=3.2, fill=True):
        cx, cy = self.p(x, y, z)
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{CYAN if fill else "#0a1317"}" stroke="{CYAN}" stroke-width="1.2"/>')

    def text(self, x, y, z, s, anchor="middle", size=11, fill=MUTED):
        cx, cy = self.p(x, y, z)
        self.add(f'<text x="{cx:.1f}" y="{cy:.1f}" class="mono" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>')

    def label(self, order, name, sub, x, y, z):
        ax, ay = self.p(x, y, z)
        self.anchors.append((order, name, sub, ax, ay))


# ── the seven illustrations ──────────────────────────────────────────────────
# Each returns an Art. Level of detail is kept low: line art, three to five elements,
# every element something the repository really contains.

def art_garage():
    a = Art(oy=300)
    t = 7
    # 01 vehicles: a low-poly vehicle on the base plate
    a.box(-68, -68, 0, 136, 136, t, inner=10)
    a.box(-44, -15, t, 82, 30, 11)                       # body
    a.box(-22, -12, t + 11, 36, 24, 11, inner=3)         # cabin
    for wx in (-30, 18):
        a.dot(wx, 15, t + 3, r=4.2, fill=False)          # near-side wheels
    # 02 documents: three sheets on the middle plate
    z2 = 62
    a.box(-68, -68, z2, 136, 136, t, inner=10)
    for i, sx in enumerate((-46, -12, 22)):
        a.box(sx, -22, z2 + t, 28, 40, 2, inner=3)
        for k in range(2):
            ca, cb = a.p(sx + 6, -14 + k * 8, z2 + t + 2), a.p(sx + 22, -14 + k * 8, z2 + t + 2)
            a.line(ca, cb, "inner")
    # 03 reminders: the 30 / 15 / 7 / 1 day runway
    z3 = 124
    a.box(-68, -68, z3, 136, 136, t, inner=10)
    xs = (-48, -22, 4, 30)
    a.line(a.p(-56, 0, z3 + t), a.p(52, 0, z3 + t), "wire")
    for i, x in enumerate(xs):
        a.dot(x, 0, z3 + t, r=3.4, fill=False)
    a.disc(52, 0, z3 + t, r=6.5, fill=True, glow=True)
    a.line(a.p(0, 0, t), a.p(0, 0, z3), "spine", dash=True)
    a.label(1, "VEHICLES", "cars · vans · buses", 68, 0, t)
    a.label(2, "DOCUMENTS", "rc · insurance · puc", 68, 0, z2 + t)
    a.label(3, "REMINDERS", "30 · 15 · 7 · 1 days", 68, 0, z3 + t)
    return a


def art_saaj():
    a = Art(oy=232)
    a.direction = "down"
    t = 2
    # a phone slab (the form) standing to the left
    ox_, oy_ = -78, 8
    def face(x, y, d, h, z=0, cls="face"):
        pp = [a.p(x, y, z), a.p(x, y + d, z), a.p(x, y + d, z + h), a.p(x, y, z + h)]
        a.add(f'<polygon points="{pts(pp)}" class="{cls}"/>')
    face(ox_, oy_, 38, 92, z=-18)
    for k in range(4):
        face_pts = [a.p(ox_, oy_ + 6, -18 + 20 + k * 15), a.p(ox_, oy_ + 32, -18 + 20 + k * 15)]
        a.line(face_pts[0], face_pts[1], "inner")
    btn = [a.p(ox_, oy_ + 8, -18 + 8), a.p(ox_, oy_ + 30, -18 + 8)]
    a.add(f'<path d="M{btn[0][0]:.1f} {btn[0][1]:.1f}L{btn[1][0]:.1f} {btn[1][1]:.1f}" stroke="{CYAN}" stroke-width="3" stroke-linecap="round"/>')
    # the five pages of the PDF, cover on top, branding last
    names = ["COVER", "SERVICES", "NOTES & TERMS", "SUMMARY", "BRANDING"]
    subs = ["client · event · date", "per-service pricing", "notes and terms", "totals, in words", "last page, always"]
    n = 5
    base_z = 0
    for i in range(n - 1, -1, -1):          # draw bottom (branding) first
        z = base_z + (n - 1 - i) * 17
        sx = -10 + (n - 1 - i) * 7
        a.box(sx, -44, z, 90, 98, t, inner=0)
        if i == 0:                         # content on the cover
            a.line(a.p(sx + 12, -30, z + t), a.p(sx + 58, -30, z + t), "bar")
            for k in range(3):
                a.line(a.p(sx + 12, -14 + k * 11, z + t), a.p(sx + 70 - (k % 2) * 16, -14 + k * 11, z + t), "inner")
        if i == 3:
            a.line(a.p(sx + 12, 36, z + t), a.p(sx + 70, 36, z + t), "bar")
    for i in range(n):
        z = (n - 1 - i) * 17
        sx = -10 + (n - 1 - i) * 7
        a.label(i + 1, names[i], subs[i], sx + 90, 5, z + t)
    a.line(a.p(-76, 54, 30), a.p(-4, 26, 66), "wire", dash=True)
    return a


def art_agent():
    a = Art(oy=292)
    t = 7
    a.box(-68, -68, 0, 136, 136, t, inner=10)
    z = t
    # the question enters at the front; sources fan out behind; the report floats above
    src = [(-46, -34), (-12, -52), (40, -40), (50, 10), (-40, 20)]
    center = (4, -4)
    ask = (28, 50)
    a.line(a.p(*ask, z), a.p(*center, z), "bar")
    for (x, y) in src:
        a.line(a.p(x, y, z), a.p(*center, z), "wire")
    a.line(a.p(*src[0], z), a.p(*src[1], z), "inner")
    a.line(a.p(*src[2], z), a.p(*src[3], z), "inner")
    a.line(a.p(*src[3], z), a.p(*src[4], z), "inner")
    for (x, y) in src:
        a.disc(x, y, z, r=6)
    a.disc(*ask, z, r=6, fill=True)
    a.disc(center[0], center[1], z, r=9, fill=True, glow=True)
    for k, (x, y) in enumerate(src[:3]):
        a.line(a.p(x, y, z + 3), a.p(x, y, z + 22), "wire", dash=True)
        a.text(x, y, z + 30, f"[{k + 1}]", size=12, fill=CYAN)
    zr = 112
    a.line(a.p(*center, z + 4), a.p(*center, zr), "spine", dash=True)
    a.box(-26, -32, zr, 60, 56, 5, inner=6)
    for k in range(3):
        a.line(a.p(-14, -18 + k * 9, zr + 5), a.p(20 - (k % 2) * 8, -18 + k * 9, zr + 5), "inner")
    a.label(1, "QUESTION", "plan · subquestions", ask[0] + 4, ask[1], z)
    a.label(2, "SOURCES", "searched and fetched", 68, 0, z)
    a.label(3, "REPORT", "every claim cited", 34, 0, zr + 5)
    return a


def art_fogai():
    a = Art(oy=300)
    t = 7
    a.box(-68, -68, 0, 136, 136, t, inner=10)
    z = t
    sensors = [(-34, 48), (-12, 48), (10, 48), (32, 48)]
    fog = (-8, -14)                       # centre of the fog node footprint
    # sensor links run back to the fog node
    for (x, y) in sensors:
        a.line(a.p(x, y, z), a.p(fog[0], fog[1] + 16, z + 4), "wire")
    # the fog node: a tall block with a soft glow
    cx, cy = a.p(fog[0], fog[1], z + 40)
    a.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="52" ry="16" fill="{CYAN}" opacity=".12"/>')
    a.box(fog[0] - 16, fog[1] - 16, z, 32, 32, 34)
    a.box(fog[0] - 16, fog[1] - 16, z + 34, 32, 32, 3, hl=True)
    for (x, y) in sensors:
        a.disc(x, y, z, r=5)
    # local action: a small block beside it, solid link
    a.box(34, -18, z, 22, 22, 14)
    a.line(a.p(fog[0] + 16, fog[1], z + 8), a.p(34, -7, z + 8), "bar")
    # the cloud: a plate floating above, dashed link
    zc = 150
    a.line(a.p(fog[0], fog[1], z + 38), a.p(fog[0], fog[1], zc), "wire", dash=True)
    a.box(-36, -52, zc, 56, 56, 4, inner=6)
    a.label(1, "SENSORS", "temp · vibration · cpu", 32, 48, z)
    a.label(2, "FOG NODE", "rules + risk score", 8, -14, z + 18)
    a.label(3, "CLOUD", "~120 ms (simulated)", 20, -24, zc + 4)
    return a


def art_journal():
    a = Art(oy=300)
    # a Merkle tree: artefacts -> hashes -> one root digest
    a.box(-68, -22, 0, 136, 44, 5, inner=6)
    z0 = 5
    xs = (-52, -18, 16, 50)
    for x in xs:
        a.box(x - 11, -11, z0, 22, 22, 12)
    zt = z0 + 12
    mid = ((-35, 46), (33, 46))
    for (x, zz) in mid:
        a.box(x - 10, -10, zz, 20, 20, 10)
    root_z = 90
    a.box(-12, -12, root_z, 24, 24, 11, hl=False)
    # edges between top faces
    for x in xs[:2]:
        a.line(a.p(x, 0, zt), a.p(-35, 0, 46), "wire")
    for x in xs[2:]:
        a.line(a.p(x, 0, zt), a.p(33, 0, 46), "wire")
    for (x, zz) in mid:
        a.line(a.p(x, 0, zz + 10), a.p(0, 0, root_z), "wire")
    # a padlock on the root
    lx, ly = a.p(0, 0, root_z + 11 + 18)
    a.add(f'<rect x="{lx - 8:.1f}" y="{ly - 4:.1f}" width="16" height="12" rx="2.5" fill="#0a1317" stroke="{CYAN}" stroke-width="1.4"/>'
          f'<path d="M{lx - 4.5:.1f} {ly - 4:.1f}v-3.5a4.5 4.5 0 0 1 9 0v3.5" fill="none" stroke="{CYAN}" stroke-width="1.4"/>')
    a.add(f'<ellipse cx="{lx:.1f}" cy="{ly + 2:.1f}" rx="26" ry="9" fill="{CYAN}" opacity=".1"/>')
    a.label(1, "ARTEFACTS", "simulator · results", 68, 0, z0)
    a.label(2, "HASHES", "blake2b per file", 43, 0, 56)
    a.label(3, "ROOT DIGEST", "frozen state", 12, 0, root_z + 11)
    return a


def art_java():
    a = Art(oy=306)
    t = 7
    # 01 the JVM: the base plate everything runs on
    a.box(-68, -68, 0, 136, 136, t, inner=10)
    z = 104
    for (x, y) in ((-60, 10), (-8, 10), (-60, 58), (-8, 58), (8, -58), (60, -58), (8, -10), (60, -10)):
        a.line(a.p(x, y, t), a.p(x, y, z), "inner")
    # 02 experiment 1: six programs in a 3x2 grid (left)
    a.box(-64, 4, z, 60, 60, 4, inner=4)
    for i in range(3):
        for j in range(2):
            a.box(-58 + i * 17, 10 + j * 23, z + 4, 12, 17, 18)
    # 03 experiment 2: one mini project (right)
    a.box(4, -64, z, 60, 60, 4, inner=4)
    a.box(18, -50, z + 4, 32, 32, 34)
    a.box(18, -50, z + 38, 32, 32, 3, hl=True)
    a.label(1, "JVM", "java 16 · javac", 68, 20, t)
    a.label(2, "EXP 1", "six console programs", -4, 34, z + 4)
    a.label(3, "EXP 2", "miniproject.java", 56, -34, z + 42)
    return a


def art_devops():
    a = Art(oy=302)
    t = 7
    a.box(-68, -68, 0, 136, 136, t, inner=10)
    z = t
    # 01 CI: commits along the front edge, with a short-lived branch
    for k, x in enumerate((-44, -26, -8, 10)):
        a.dot(x, 46, z, r=3.6, fill=(k == 3))
    a.line(a.p(-44, 46, z), a.p(10, 46, z), "wire")
    a.line(a.p(-26, 46, z), a.p(-18, 34, z), "wire")
    a.dot(-18, 34, z, r=3, fill=False)
    # 02 images: three container blocks
    for x in (-50, -26, -2):
        a.box(x, -10, z, 18, 24, 28)
        a.line(a.p(x + 2, -6, z + 28), a.p(x + 16, -6, z + 28), "inner")
        a.line(a.p(x + 2, 2, z + 28), a.p(x + 16, 2, z + 28), "inner")
    a.line(a.p(-18, 34, z), a.p(-18, 16, z), "bar")
    # 03 cluster: eight workloads on a raised plate
    zc = 120
    a.box(-18, -62, zc, 62, 62, 4, inner=3)
    for i in range(2):
        for j in range(4):
            a.box(-10 + i * 26, -56 + j * 14, zc + 4, 16, 10, 12)
    for x in (-42, -18, 6):
        a.line(a.p(x + 9, -10, z + 28), a.p(-8 + (x + 42) * 0.5, -10, zc), "spine", dash=True)
    a.label(1, "CI", "actions · terraform", 10, 46, z)
    a.label(2, "IMAGES", "pushed to acr", 16, 2, z + 18)
    a.label(3, "CLUSTER", "aks · 8 workloads", 44, -30, zc + 4)
    return a


# ── copy + status for each banner ────────────────────────────────────────────
BANNERS = [
    {
        "slug": "saaj-garage", "title": "SAAJ Garage", "kicker": "FLEET MANAGEMENT",
        "desc": ["A private fleet manager for a family transport", "business: vehicles, documents and renewals."],
        "stack": "react · typescript · supabase · vercel", "meta": ("repo", "private · single owner"),
        "status": "private", "art": art_garage, "node": "05",
    },
    {
        "slug": "saaj", "title": "Saaj", "kicker": "QUOTATION PDF MAKER",
        "desc": ["A mobile-first quotation maker for an events", "business. The PDF is built on the device."],
        "stack": "react · typescript · vite · react-pdf", "meta": ("repo", "private · no backend"),
        "status": "private", "art": art_saaj, "node": "06",
    },
    {
        "slug": "ai-research-agent", "title": "AI Research Agent", "kicker": "AI RESEARCH PIPELINE",
        "desc": ["A bounded research agent that plans, searches,", "verifies and cites every claim to a real source."],
        "stack": "python · fastapi · react · docker", "meta": ("repo", "public · MIT"),
        "status": "public", "art": art_agent, "node": "03",
    },
    {
        "slug": "FogAi", "title": "FogAI", "kicker": "FOG COMPUTING · INDUSTRIAL IOT",
        "desc": ["Safety-critical IoT decisions made on the fog node,", "not on a cloud round trip. Simulated end to end."],
        "stack": "python · numpy · flask · rich", "meta": ("scope", "simulation · IEEE paper source"),
        "status": "public", "art": art_fogai, "node": "01",
    },
    {
        "slug": "fogai-journal-v2", "title": "FogAI Journal", "kicker": "RESEARCH ARCHIVE",
        "desc": ["A pre-registered, sealed-holdout evaluation of", "learned fog/cloud task placement."],
        "stack": "python · scikit-learn · numpy · scipy", "meta": ("repo", "private · manuscript in preparation"),
        "status": "private", "art": art_journal, "node": "02",
    },
    {
        "slug": "JavaFullStack-WIPRO", "title": "JavaFullStack-WIPRO", "kicker": "CORE JAVA",
        "desc": ["Java exercises by experiment: console programs", "and a command-line salary mini project."],
        "stack": "java 16 · eclipse", "meta": ("status", "in progress · core java only"),
        "status": "wip", "art": art_java, "node": "07",
    },
    {
        "slug": "sree-saaj-devops-", "title": "Sree-SAAJ DevOps", "kicker": "CLOUD · CONTAINERS · CI/CD",
        "desc": ["A microservices platform on Azure: Docker, Terraform,", "Kubernetes manifests and GitHub Actions."],
        "stack": "docker · terraform · kubernetes · ansible", "meta": ("repo", "public · azure (acr, aks)"),
        "status": "public", "art": art_devops, "node": "04",
    },
]

STYLE = f"""
    .sans {{ font-family: {SANS}; }}
    .mono {{ font-family: {MONO}; }}
    .face {{ fill: #0a1317; stroke: {CYAN_DEEP}; stroke-width: 1.1; stroke-linejoin: round; }}
    .hl {{ fill: rgba(63, 224, 238, .16); stroke: {CYAN}; stroke-width: 1.3; stroke-linejoin: round; }}
    .inner {{ fill: none; stroke: #15303a; stroke-width: 1; }}
    .side-l {{ fill: #070d10; stroke: #1a3a41; stroke-width: 1; stroke-linejoin: round; }}
    .side-r {{ fill: #091216; stroke: #1a3a41; stroke-width: 1; stroke-linejoin: round; }}
    .wire {{ stroke: {CYAN_DEEP}; stroke-width: 1.3; fill: none; }}
    .bar {{ stroke: {CYAN}; stroke-width: 1.8; stroke-linecap: round; fill: none; }}
    .spine {{ stroke: #26414a; stroke-width: 1; fill: none; }}
    .lead {{ stroke: #26414a; stroke-width: 1; fill: none; }}
    .name {{ font-size: 12.5px; fill: #c3ccd6; letter-spacing: .14em; }}
    .sub {{ font-size: 11.5px; fill: #56636f; letter-spacing: .02em; }}
"""

LABEL_X = 1002
MIN_GAP = 44


def place_labels(anchors):
    """Order by screen y, then push apart so the label column never collides."""
    items = sorted(anchors, key=lambda a: a[4])
    ys = [a[4] for a in items]
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + MIN_GAP)
    over = ys[-1] - 322
    if over > 0:
        ys = [y - over for y in ys]
        for i in range(len(ys) - 2, -1, -1):
            ys[i] = min(ys[i], ys[i + 1] - MIN_GAP)
    return list(zip(items, ys))


def build(b):
    art = b["art"]()
    labels = []
    placed = place_labels(art.anchors)
    total = len(placed)
    for rank, ((_o, name, sub, ax, ay), ly) in enumerate(placed):
        order = total - rank if art.direction == "up" else rank + 1
        labels.append(
            f'<g><path d="M{ax + 6:.1f} {ay:.1f}H{min(ax + 20, 986):.1f}L992 {ly:.1f}H996" class="lead"/>'
            f'<text x="{LABEL_X}" y="{ly + 1:.1f}" class="mono name">{order:02d}&#160;&#160;{escape(name)}</text>'
            f'<text x="{LABEL_X}" y="{ly + 16:.1f}" class="mono sub">{escape(sub)}</text></g>')

    # status, top right
    if b["status"] == "private":
        status = (f'<g class="mono" font-size="12" letter-spacing=".14em" fill="{MUTED}">'
                  f'<rect x="1049" y="57.5" width="10" height="8" rx="1.8" fill="{MUTED}"/>'
                  f'<path d="M1051.2 57.5v-2.8a2.8 2.8 0 0 1 5.6 0v2.8" fill="none" stroke="{MUTED}" stroke-width="1.4"/>'
                  f'<text x="1136" y="66" text-anchor="end">PRIVATE</text></g>')
    elif b["status"] == "wip":
        status = (f'<g class="mono" font-size="12" letter-spacing=".14em" fill="{AMBER}">'
                  f'<circle cx="1022" cy="62" r="3.5" fill="{AMBER}"/>'
                  f'<text x="1136" y="66" text-anchor="end">IN PROGRESS</text></g>')
    else:
        status = (f'<g class="mono" font-size="12" letter-spacing=".14em" fill="{CYAN}">'
                  f'<circle cx="1068" cy="62" r="3.5" fill="{CYAN}"/>'
                  f'<text x="1136" y="66" text-anchor="end">PUBLIC</text></g>')

    title_len = len(b["title"]) * 58 * 0.545
    alt = (f'{b["title"]}: {" ".join(b["desc"])} Stack: {b["stack"].replace(" · ", ", ")}. '
           f'{"Private repository." if b["status"] == "private" else ""}')
    mkey, mval = b["meta"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
  <title id="t">{escape(alt.strip())}</title>
  <defs>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#0f161e" stroke-width="1"/></pattern>
    <radialGradient id="glow" cx="860" cy="196" r="270" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{CYAN}" stop-opacity=".14"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
    <linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{BG}" stop-opacity=".92"/><stop offset=".5" stop-color="{BG}" stop-opacity=".55"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
  </defs>
  <style>{STYLE}  </style>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
    <rect width="700" height="{H}" fill="url(#fade)"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{EDGE}"/>
  <g stroke="#2a3542" stroke-width="1.2" fill="none"><path d="M28 44V28H44M1156 28H1172V44M1172 336V352H1156M44 352H28V336"/></g>
  <path d="M64 340H640" stroke="#141b23"/>

  <text class="mono" x="64" y="66" font-size="12" fill="{FAINT}" letter-spacing=".12em">~/{escape(b["slug"])}</text>
  <text class="mono" x="64" y="128" font-size="13" fill="{CYAN}" letter-spacing=".22em">{escape(b["kicker"]).replace(" · ", " &#183; ")}</text>
  <text class="sans" x="62" y="190" font-size="58" font-weight="600" fill="{TEXT}" letter-spacing="-.01em" textLength="{title_len:.0f}" lengthAdjust="spacingAndGlyphs">{escape(b["title"])}</text>
  <text class="sans" x="64" y="232" font-size="20" fill="{MUTED}">{escape(b["desc"][0])}</text>
  <text class="sans" x="64" y="256" font-size="20" fill="{MUTED}">{escape(b["desc"][1])}</text>
  <g class="mono" font-size="13" fill="{DIM}">
    <text x="64" y="297">stack&#160;&#160;&#160;<tspan fill="#9aa6b3">{escape(b["stack"]).replace(" · ", " &#183; ")}</tspan></text>
    <text x="64" y="319">{escape(mkey).ljust(6).replace(" ", "&#160;")}&#160;&#160;<tspan fill="#9aa6b3">{escape(mval).replace(" · ", " &#183; ")}</tspan></text>
  </g>
  {status}

  <g>{"".join(art.parts)}</g>
  {"".join(labels)}
</svg>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="banners", help="directory for <slug>.svg files")
    ap.add_argument("--repos-root", help="parent folder of the repo clones; writes <root>/<slug>/assets/readme/banner.svg")
    args = ap.parse_args()
    for b in BANNERS:
        svg = build(b)
        if args.repos_root:
            dest = Path(args.repos_root) / b["slug"] / "assets" / "readme" / "banner.svg"
        else:
            dest = Path(args.out) / f"{b['slug']}.svg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(svg, encoding="utf-8", newline="\n")
        print(f"{b['slug']:22s} {len(svg):6d} bytes -> {dest}")


if __name__ == "__main__":
    main()
