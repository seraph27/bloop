#!/usr/bin/env python3
"""Daily README generator: portfolio prices, world news, git activity."""
import subprocess
import sys
import xml.etree.ElementTree as ET
import urllib.request
from datetime import date, datetime
from pathlib import Path

TICKERS = [
    "NVDA", "SPGI", "META", "AAPL", "MSFT", "GOOG",
    "TSM", "IONQ", "COST", "ASML", "SPYM", "LLY",
    "OKLO", "V", "MA", "AMZN", "DUOL",
]

REPO_SEARCH_DIRS = [Path.home() / d for d in ("Documents", "Projects", "code", "dev", "src")]


def ensure_deps():
    try:
        import yfinance  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "-q", "--user"])


def fetch_stocks():
    import yfinance as yf
    rows = []
    tickers = yf.Tickers(" ".join(TICKERS))
    for symbol in TICKERS:
        t = tickers.tickers[symbol]
        fi = t.fast_info
        price = fi.last_price or 0
        prev = fi.previous_close or price
        pct = (price - prev) / prev * 100 if prev else 0
        arrow = "▲" if pct >= 0 else "▼"
        rows.append(f"| {symbol:<5} | ${price:>9.2f} | {arrow} {pct:+.2f}% |")
    return rows


def fetch_news(limit=6):
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    with urllib.request.urlopen(url, timeout=10) as resp:
        tree = ET.parse(resp)
    items = tree.findall(".//item")[:limit]
    return [(item.findtext("title", ""), item.findtext("link", "")) for item in items]


def fetch_git_activity():
    repos = []
    for base in REPO_SEARCH_DIRS:
        if base.is_dir():
            for p in base.iterdir():
                if (p / ".git").is_dir():
                    repos.append(p)
            if (base / ".git").is_dir():
                repos.append(base)

    today = date.today().strftime("%Y-%m-%d")
    activity = []
    for repo in repos:
        result = subprocess.run(
            ["git", "-C", str(repo), "log", "--oneline", f"--since={today} 00:00", "--all"],
            capture_output=True, text=True,
        )
        lines = [l for l in result.stdout.strip().splitlines() if l]
        if lines:
            activity.append((repo.name, lines[:6]))
    return activity


def build_readme(stocks, news, git_activity):
    today = date.today().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M")

    sections = [
        f"# bloop — {today}\n",
        f"*{now} daily snapshot*\n",
        "\n## Portfolio\n",
        "| Ticker | Price     | Day %     |\n|--------|-----------|-----------|",
        *stocks,
        "\n## World News\n",
        *[f"- [{title}]({link})" for title, link in news],
    ]

    if git_activity:
        sections += ["\n## Git Activity\n"]
        for repo, commits in git_activity:
            sections.append(f"**{repo}**")
            sections += [f"- `{c}`" for c in commits]

    return "\n".join(sections) + "\n"


if __name__ == "__main__":
    ensure_deps()
    stocks = fetch_stocks()
    news = fetch_news()
    git_activity = fetch_git_activity()
    readme = build_readme(stocks, news, git_activity)
    Path(__file__).parent.joinpath("README.md").write_text(readme)
    print("README updated")
