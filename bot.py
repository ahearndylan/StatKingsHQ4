import tweepy
from nba_api.stats.endpoints import leaguedashplayerstats
from datetime import datetime
import requests
import json
import os

# ======================= #
# TWITTER AUTHENTICATION  #
# ======================= #
bearer_token = "AAAAAAAAAAAAAAAAAAAAAPztzwEAAAAAvBGCjApPNyqj9c%2BG7740SkkTShs%3DTCpOQ0DMncSMhaW0OA4UTPZrPRx3BHjIxFPzRyeoyMs2KHk6hM"
api_key = "uKyGoDr5LQbLvu9i7pgFrAnBr"
api_secret = "KGBVtj1BUmAEsyoTmZhz67953ItQ8TIDcChSpodXV8uGMPXsoH"
access_token = "1901441558596988929-WMdEPOtNDj7QTJgLHVylxnylI9ObgD"
access_token_secret = "9sf83R8A0MBdijPdns6nWaG7HF47htcWo6oONPmMS7o98"

client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# ======================= #
#   SUPABASE CONFIG       #
# ======================= #
SUPABASE_URL = "https://fjtxowbjnxclzcogostk.supabase.co/rest/v1/seasonkings"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqdHhvd2JqbnhjbHpjb2dvc3RrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDI2MDE5NTgsImV4cCI6MjA1ODE3Nzk1OH0.LPkFw-UX6io0F3j18Eefd1LmeAGGXnxL4VcCLOR_c1Q"

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# ======================= #
#     NBA STATS LOGIC     #
# ======================= #

def get_season_leaders():
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season="2024-25",
        season_type_all_star="Regular Season"
    )
    players = stats.get_normalized_dict()["LeagueDashPlayerStats"]

    # Filter out players with 0 games just in case, then sort by total points
    filtered_players = [p for p in players if p["GP"] > 0]
    top_players = sorted(filtered_players, key=lambda x: x["PTS"], reverse=True)[:4]

    player_info = []
    for player in top_players:
        name = player["PLAYER_NAME"]
        team = player["TEAM_ABBREVIATION"]
        gp = player["GP"]
        total_points = int(player["PTS"])
        ppg = round(total_points / gp, 1) if gp > 0 else 0.0
        player_info.append((name, team, ppg, total_points))

    return player_info

def compose_tweet(player_info):
    tweet = "👑 Season Scoring Leaders\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, team, ppg, total_points) in enumerate(player_info, 1):
        rank = medals[i - 1] if i <= 3 else f"{i}."
        tweet += f"{rank} {name} ({team}): {total_points} PTS | {ppg} PPG\n\n"
    tweet += "#NBA #StatKingsHQ"
    return tweet

def update_supabase_season_data(player_info):
    date_str = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "date": date_str,
        "data": {
            "leaders": [
                {
                    "name": name,
                    "team": team,
                    "ppg": ppg,
                    "points": total_points
                } for name, team, ppg, total_points in player_info
            ]
        }
    }

    res = requests.post(SUPABASE_URL, headers=HEADERS, data=json.dumps(payload))
    if res.status_code in (200, 201):
        print(f"✅ Supabase updated: {res.json()}")
    else:
        print("❌ Supabase write error:", res.text)

# ======================= #
#        MAIN BOT         #
# ======================= #

def run_bot():
    try:
        player_info = get_season_leaders()
        tweet = compose_tweet(player_info)
        print("Tweeting:\n", tweet)
        client.create_tweet(text=tweet)
        update_supabase_season_data(player_info)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    run_bot()
