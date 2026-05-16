import os
import uuid
import requests
from datetime import datetime, timezone

API_KEY = os.environ.get("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}
WC_ID = 2000  # ID del Mundial en football-data.org

def fetch_matches():
    url = f"{BASE_URL}/competitions/{WC_ID}/matches"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("matches", [])

def score_str(match):
    status = match.get("status")
    score = match.get("score", {})
    ft = score.get("fullTime", {})
    home = ft.get("home")
    away = ft.get("away")
    if status == "FINISHED" and home is not None and away is not None:
        return f" [{home}-{away}]"
    elif status == "IN_PLAY" or status == "PAUSED":
        half = score.get("halfTime", {})
        hh = half.get("home")
        ha = half.get("away")
        if hh is not None:
            return f" [EN JUEGO {hh}-{ha}]"
        return " [EN JUEGO]"
    return ""

def make_event(match):
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    status = match.get("status", "")
    stage = match.get("stage", "")
    group = match.get("group") or stage

    result = score_str(match)
    summary = f"⚽ {home} vs. {away}{result}"

    utc_date = match.get("utcDate", "")
    try:
        dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
        dtstart = dt.strftime("%Y%m%dT%H%M%SZ")
    except:
        dtstart = "19700101T000000Z"

    uid = str(uuid.uuid5(uuid.NAMESPACE_URL, str(match["id"])))
    venue = match.get("venue") or "Estadio por confirmar"
    desc = f"Copa del Mundo 2026 - {group}"
    if status == "FINISHED":
        ft = match["score"]["fullTime"]
        desc += f"\\nResultado final: {ft['home']}-{ft['away']}"

    return f"""BEGIN:VEVENT
UID:{uid}@mundial2026
DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{dtstart}
SUMMARY:{summary}
LOCATION:{venue}
DESCRIPTION:{desc}
END:VEVENT"""

def generate_ics(matches):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Mundial 2026//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Mundial 2026 🏆",
        "X-WR-TIMEZONE:Europe/Madrid",
        "X-WR-CALDESC:Calendario oficial Copa del Mundo 2026 - Actualización automática",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
    ]
    for m in matches:
        lines.append(make_event(m))
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

if __name__ == "__main__":
    print("Obteniendo partidos...")
    matches = fetch_matches()
    print(f"Total partidos: {len(matches)}")
    ics = generate_ics(matches)
    os.makedirs("docs", exist_ok=True)
    with open("docs/mundial2026.ics", "w", encoding="utf-8") as f:
        f.write(ics)
    print("Archivo generado: docs/mundial2026.ics")
