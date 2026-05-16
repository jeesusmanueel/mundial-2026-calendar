import os
import uuid
import requests
from datetime import datetime, timezone

API_KEY = os.environ.get("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}
WC_ID = 2000

VENUES = {
    "Mexico vs South Africa": "Estadio Azteca, Ciudad de México",
    "South Korea vs Czechia": "Estadio Akron, Guadalajara",
    "Czechia vs South Africa": "Mercedes-Benz Stadium, Atlanta",
    "Mexico vs South Korea": "Estadio Akron, Guadalajara",
    "Czechia vs Mexico": "Estadio Azteca, Ciudad de México",
    "South Africa vs South Korea": "Estadio BBVA, Monterrey",
    "Canada vs Bosnia and Herzegovina": "BMO Field, Toronto",
    "Qatar vs Switzerland": "Levi's Stadium, San Francisco",
    "Switzerland vs Bosnia and Herzegovina": "SoFi Stadium, Los Ángeles",
    "Canada vs Qatar": "BC Place, Vancouver",
    "Switzerland vs Canada": "BC Place, Vancouver",
    "Bosnia and Herzegovina vs Qatar": "Lumen Field, Seattle",
    "Brazil vs Morocco": "MetLife Stadium, Nueva Jersey",
    "Haiti vs Scotland": "Gillette Stadium, Boston",
    "Scotland vs Morocco": "Gillette Stadium, Boston",
    "Brazil vs Haiti": "Lincoln Financial Field, Philadelphia",
    "Scotland vs Brazil": "Hard Rock Stadium, Miami",
    "Morocco vs Haiti": "Mercedes-Benz Stadium, Atlanta",
    "United States vs Paraguay": "SoFi Stadium, Los Ángeles",
    "United States vs Australia": "Lumen Field, Seattle",
    "Paraguay vs Australia": "Levi's Stadium, San Francisco",
    "Germany vs Curaçao": "NRG Stadium, Houston",
    "Côte d'Ivoire vs Ecuador": "Lincoln Financial Field, Philadelphia",
    "Germany vs Côte d'Ivoire": "BMO Field, Toronto",
    "Curaçao vs Ecuador": "Arrowhead Stadium, Kansas City",
    "Ecuador vs Germany": "MetLife Stadium, Nueva Jersey",
    "Curaçao vs Côte d'Ivoire": "Lincoln Financial Field, Philadelphia",
    "Netherlands vs Japan": "AT&T Stadium, Dallas",
    "Netherlands vs TBD": "NRG Stadium, Houston",
    "Tunisia vs Japan": "Estadio BBVA, Monterrey",
    "Japan vs TBD": "AT&T Stadium, Dallas",
    "Tunisia vs Netherlands": "Arrowhead Stadium, Kansas City",
    "Iran vs New Zealand": "SoFi Stadium, Los Ángeles",
    "Belgium vs Egypt": "Lumen Field, Seattle",
    "Belgium vs Iran": "SoFi Stadium, Los Ángeles",
    "New Zealand vs Egypt": "BC Place, Vancouver",
    "Egypt vs Iran": "Lumen Field, Seattle",
    "New Zealand vs Belgium": "BC Place, Vancouver",
    "Spain vs Cape Verde": "Mercedes-Benz Stadium, Atlanta",
    "Saudi Arabia vs Uruguay": "Hard Rock Stadium, Miami",
    "Spain vs Saudi Arabia": "Mercedes-Benz Stadium, Atlanta",
    "Uruguay vs Cape Verde": "Hard Rock Stadium, Miami",
    "Cape Verde vs Saudi Arabia": "NRG Stadium, Houston",
    "Uruguay vs Spain": "Estadio Akron, Guadalajara",
    "France vs Senegal": "MetLife Stadium, Nueva Jersey",
    "Norway vs Senegal": "MetLife Stadium, Nueva Jersey",
    "Norway vs France": "Gillette Stadium, Boston",
    "Argentina vs Algeria": "Arrowhead Stadium, Kansas City",
    "Austria vs Jordan": "Levi's Stadium, San Francisco",
    "Argentina vs Austria": "AT&T Stadium, Dallas",
    "Jordan vs Algeria": "Levi's Stadium, San Francisco",
    "Algeria vs Austria": "Arrowhead Stadium, Kansas City",
    "Jordan vs Argentina": "AT&T Stadium, Dallas",
    "Uzbekistan vs Colombia": "Estadio Azteca, Ciudad de México",
    "Portugal vs Uzbekistan": "NRG Stadium, Houston",
    "Colombia vs Portugal": "Hard Rock Stadium, Miami",
    "England vs Croatia": "AT&T Stadium, Dallas",
    "Ghana vs Panama": "BMO Field, Toronto",
    "England vs Ghana": "Gillette Stadium, Boston",
    "Panama vs Croatia": "BMO Field, Toronto",
    "Panama vs England": "MetLife Stadium, Nueva Jersey",
    "Croatia vs Ghana": "Lincoln Financial Field, Philadelphia",
}

KNOCKOUT_VENUES = {
    1: "SoFi Stadium, Los Ángeles",
    2: "NRG Stadium, Houston",
    3: "Estadio BBVA, Monterrey",
    4: "Gillette Stadium, Boston",
    5: "MetLife Stadium, Nueva Jersey",
    6: "AT&T Stadium, Dallas",
    7: "Estadio Azteca, Ciudad de México",
    8: "Mercedes-Benz Stadium, Atlanta",
    9: "Levi's Stadium, San Francisco",
    10: "Lumen Field, Seattle",
    11: "BMO Field, Toronto",
    12: "SoFi Stadium, Los Ángeles",
    13: "BC Place, Vancouver",
    14: "Hard Rock Stadium, Miami",
    15: "Arrowhead Stadium, Kansas City",
    16: "AT&T Stadium, Dallas",
}

def fetch_matches():
    url = f"{BASE_URL}/competitions/{WC_ID}/matches"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("matches", [])

def get_venue(match, index):
    home = match["homeTeam"].get("name", "")
    away = match["awayTeam"].get("name", "")
    key = f"{home} vs {away}"
    if key in VENUES:
        return VENUES[key]
    key2 = f"{away} vs {home}"
    if key2 in VENUES:
        return VENUES[key2]
    stage = match.get("stage", "")
    if stage != "GROUP_STAGE" and index in KNOCKOUT_VENUES:
        return KNOCKOUT_VENUES[index]
    return "Estadio por confirmar"

def score_str(match):
    status = match.get("status")
    score = match.get("score", {})
    ft = score.get("fullTime", {})
    home = ft.get("home")
    away = ft.get("away")
    if status == "FINISHED" and home is not None and away is not None:
        return f" [{home}-{away}]"
    elif status in ("IN_PLAY", "PAUSED"):
        half = score.get("halfTime", {})
        hh = half.get("home")
        ha = half.get("away")
        if hh is not None:
            return f" [EN JUEGO {hh}-{ha}]"
        return " [EN JUEGO]"
    return ""

def make_event(match, index):
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
    venue = get_venue(match, index)
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
    for i, m in enumerate(matches, 1):
        lines.append(make_event(m, i))
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

if __name__ == "__main__":
    print("Obteniendo partidos...")
    matches = fetch_matches()
    print(f"Total partidos: {len(matches)}")
    for m in matches[:6]:
        home = m["homeTeam"].get("name", "")
        away = m["awayTeam"].get("name", "")
        print(f'"{home} vs {away}"')
    ics = generate_ics(matches)
    os.makedirs("docs", exist_ok=True)
    with open("docs/mundial2026.ics", "w", encoding="utf-8") as f:
        f.write(ics)
    print("Archivo generado: docs/mundial2026.ics")
