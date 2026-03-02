#!/usr/bin/env python3
"""Generates a daily TL;DR: portfolio prices, global news, git activity."""

import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import yfinance as yf
from datetime import date
from pathlib import Path

TICKERS = [
    "NVDA", "SPGI", "META", "AAPL", "MSFT", "GOOG",
    "TSM", "IONQ", "COST", "ASML", "SPYM", "LLY",
    "OKLO", "V", "MA", "AMZN", "DUOL",
]

REPO_ROOT = Path(__file__).parent


def fetch_stocks() -> str:
    data = yf.download(TICKERS, period="2d", auto_adjust=True, progress=False)["Close"]
    rows = ["| Ticker | Price | Change |", "|--------|------:|-------:|"]
    for sym in TICKERS:
        try:
            series = data[sym].dropna()
            price, prev = float(series.iloc[-1]), float(series.iloc[-2])
            change = price - prev
            pct = change / prev * 100
            arrow = "▲" if change >= 0 else "▼"
            rows.append(f"| {sym:<5} | ${price:>9.2f} | {arrow} {change:+.2f} ({pct:+.2f}%) |")
        except Exception:
            rows.append(f"| {sym:<5} | — | — |")
    return "\n".join(rows)


def fetch_news() -> str:
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        tree = ET.parse(r)
    items = tree.findall(".//item")[:7]
    return "\n".join(f"- {item.find('title').text}" for item in items)


def git_activity() -> str:
    today = date.today().isoformat()
    lines = []

    candidates = list(Path.home().glob("*")) + list(Path.home().glob("*/*"))
    repos = [p for p in candidates if (p / ".git").is_dir()]

    for repo in sorted(repos):
        result = subprocess.run(
            ["git", "log", "--oneline", f"--after={today} 00:00"],
            cwd=repo, capture_output=True, text=True,
        )
        commits = [l for l in result.stdout.strip().splitlines() if l]
        if commits:
            lines.append(f"**{repo.name}** — {len(commits)} commit(s)")
            for c in commits[:3]:
                lines.append(f"  - `{c}`")

    return "\n".join(lines) if lines else "_No commits today yet._"


def build_readme() -> str:
    today = date.today().strftime("%B %d, %Y")
    sections = [
        f"# Daily TL;DR — {today}",
        "## Portfolio\n" + fetch_stocks(),
        "## Global News\n" + fetch_news(),
        "## Git Activity\n" + git_activity(),
        f"---\n_Updated {date.today().isoformat()}_",
    ]
    return "\n\n".join(sections) + "\n"


if __name__ == "__main__":
    readme = build_readme()
    (REPO_ROOT / "README.md").write_text(readme)
    print(readme)
