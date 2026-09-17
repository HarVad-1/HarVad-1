"""Render a GitHub-style streak card: python streak.py <user> <out.svg> (needs GITHUB_TOKEN)."""
import base64, json, os, re, sys, urllib.parse, urllib.request
from datetime import date, timedelta

TEXT = "0123456789"


def get(url, data=None, headers={}):
    return urllib.request.urlopen(urllib.request.Request(url, data, headers)).read()


def streak(user):
    q = 'query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}'
    res = json.loads(get("https://api.github.com/graphql", json.dumps({"query": q, "variables": {"u": user}}).encode(),
                         {"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"}))
    weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    counts = {d["date"]: d["contributionCount"] for w in weeks for d in w["contributionDays"]}
    return count_streak(counts, date.fromisoformat(max(counts)))


def count_streak(counts, today):
    # like Duolingo: today not done yet doesn't break the streak
    day = today if counts.get(today.isoformat()) else today - timedelta(days=1)
    n = 0
    while counts.get(day.isoformat()):
        n, day = n + 1, day - timedelta(days=1)
    return n


def font():
    css = get("https://fonts.googleapis.com/css2?family=Mona+Sans:wght@800&text=" + urllib.parse.quote(TEXT)).decode()
    return base64.b64encode(get(re.search(r"url\((.+?)\)", css).group(1))).decode()


def svg(n):
    # ponytail: digit width is an estimate for Mona Sans 800, card width follows digit count
    w = 32 + len(str(n)) * 102 + 24 + 153 + 32
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="240" viewBox="0 0 {w} 240">
<style>@font-face{{font-family:M;src:url(data:font/ttf;base64,{font()})}}</style>
<rect x="0.5" y="0.5" width="{w - 1}" height="239" rx="6" fill="#0d1117" stroke="#30363d"/>
<text x="32" y="174" font-family="M,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif" font-weight="800" font-size="150" fill="#e6edf3">{n}</text>
<g transform="translate({w - 32 - 153} 30) scale(0.82)">
<path d="M58 0c10 12 18 26 18 36a12 12 0 0 1-24 0c0-10 3-24 6-36z" fill="#39d353"/>
<path d="M20 70c14 0 28 8 38 14L112 18c8-8 16-8 22 0l30 40c14 18 22 40 22 68 0 52-42 94-94 94S0 178 0 126V88c0-10 8-18 20-18z" fill="#39d353"/>
<path d="M92 116c6-8 12-8 18 0l24 32c6 8 10 16 10 26 0 24-18 40-40 40s-40-16-40-40c0-10 4-18 10-26z" fill="#0e4429"/>
</g>
</svg>"""


if __name__ == "__main__":
    assert count_streak({"2026-09-16": 2, "2026-09-17": 0, "2026-09-15": 1, "2026-09-13": 4}, date(2026, 9, 17)) == 2
    assert count_streak({"2026-09-17": 1, "2026-09-16": 1}, date(2026, 9, 17)) == 2
    assert count_streak({"2026-09-15": 1}, date(2026, 9, 17)) == 0
    open(sys.argv[2], "w").write(svg(streak(sys.argv[1])))
