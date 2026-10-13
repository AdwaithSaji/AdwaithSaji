"""Render assets for the 'Activity' section: a weekly contribution trace.

Run by .github/workflows/telemetry.yml; publishes to the `output` branch.
Local run:  GITHUB_TOKEN=$(gh auth token) python scripts/telemetry.py --user AdwaithSaji --out dist/telemetry.svg
Stdlib only. Reads public profile data; never writes anything but --out.
"""
import argparse
import datetime as dt
import json
import math
import os
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

API = "https://api.github.com"
MONO = "'JetBrains Mono', 'SFMono-Regular', 'Cascadia Code', Consolas, 'Liberation Mono', Menlo, monospace"

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount } }
      }
    }
  }
}"""


def request(url: str, token: str, body: dict | None = None):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-telemetry",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch(user: str, token: str) -> dict:
    data = request(f"{API}/graphql", token, {"query": QUERY, "variables": {"login": user}})
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [(w["firstDay"], sum(d["contributionCount"] for d in w["contributionDays"])) for w in cal["weeks"]]
    repos = request(f"{API}/users/{user}/repos?per_page=100&type=owner", token)
    public = sum(1 for r in repos if not r["fork"])
    return {"total": cal["totalContributions"], "weeks": weeks, "repos": public}


def render(stats: dict, today: dt.date) -> str:
    w, h = 1200, 300
    left, right, top, base = 64, 1136, 92, 212
    weeks = stats["weeks"]
    counts = [c for _, c in weeks]
    peak = max(counts) or 1
    step = (right - left) / max(len(counts) - 1, 1)

    # sqrt scale keeps quiet weeks visible next to a busy one
    pts = [(left + i * step, base - (base - top) * math.sqrt(c / peak)) for i, c in enumerate(counts)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = f"{line} L{right:.1f} {base} L{left} {base} Z"
    lx, ly = pts[-1]

    months, seen = [], set()
    for i, (first, _) in enumerate(weeks):
        d = dt.date.fromisoformat(first)
        key = (d.year, d.month)
        if key not in seen and d.day <= 7 and 0 < i < len(weeks) - 2:
            seen.add(key)
            x = left + i * step
            months.append(f'<path d="M{x:.1f} {base}v5" stroke="#26313d"/>'
                          f'<text x="{x:.1f}" y="{base + 20}" text-anchor="middle">{d.strftime("%b").upper()}</text>')

    active = sum(1 for c in counts if c)
    readouts = [
        (f"{stats['total']}", "contributions · 12 mo"),
        (f"{active}/{len(counts)}", "active weeks"),
        (f"{peak}", "peak week"),
        (f"{stats['repos']}", "public repos"),
    ]
    cells = "".join(
        f'<text x="{left + i * 268}" y="270"><tspan fill="#e8edf2" font-size="15">{escape(v)}</tspan>'
        f'<tspan dx="10" fill="#5b6878">{escape(k)}</tspan></text>'
        for i, (v, k) in enumerate(readouts)
    )
    gridlines = "".join(f'<path d="M{left} {y:.1f}H{right}" stroke="#10171f"/>'
                        for y in (top, (top + base) / 2, base))
    summary = (f"Weekly GitHub contributions for the last 12 months: {stats['total']} total, "
               f"{active} active weeks, peak {peak} in one week, {stats['repos']} public repositories. "
               f"Updated {today.isoformat()}.")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t">
  <title id="t">{escape(summary)}</title>
  <style>
    text {{ font-family: {MONO}; font-size: 11px; fill: #5b6878; letter-spacing: .06em; }}
    .trace {{ stroke-dasharray: 1000; stroke-dashoffset: 0; animation: draw 3.2s cubic-bezier(.4,0,.2,1) both; }}
    .fill {{ animation: fade 3.2s ease-out both; }}
    .head {{ animation: beat 2.4s ease-in-out infinite; }}
    @keyframes draw {{ from {{ stroke-dashoffset: 1000; }} }}
    @keyframes fade {{ from {{ opacity: 0; }} 60% {{ opacity: 0; }} }}
    @keyframes beat {{ 50% {{ opacity: .2; }} }}
    @media (prefers-reduced-motion: reduce) {{ .trace, .fill, .head {{ animation: none; }} }}
  </style>
  <defs>
    <linearGradient id="a" x1="0" y1="{top}" x2="0" y2="{base}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#3fe0ee" stop-opacity=".22"/><stop offset="1" stop-color="#3fe0ee" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="#07090c" stroke="#1a222d"/>
  <text x="{left}" y="52" letter-spacing=".2em"><tspan fill="#3fe0ee">SIGNAL TRACE</tspan>  ·  contributions per week, sqrt scale</text>
  <text x="{right}" y="52" text-anchor="end">updated {today.isoformat()}</text>
  {gridlines}
  <g>{"".join(months)}</g>
  <path class="fill" d="{area}" fill="url(#a)"/>
  <path class="trace" d="{line}" pathLength="1000" fill="none" stroke="#3fe0ee" stroke-width="1.6" stroke-linejoin="round"/>
  <circle class="head" cx="{lx:.1f}" cy="{ly:.1f}" r="8" fill="#3fe0ee" opacity=".35"/>
  <circle cx="{lx:.1f}" cy="{ly:.1f}" r="3" fill="#3fe0ee"/>
  <path d="M{left} 244.5H{right}" stroke="#141b23"/>
  {cells}
</svg>
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--user", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(fetch(args.user, token), dt.date.today()), encoding="utf-8", newline="\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
