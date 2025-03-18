import tweepy
from nba_api.stats.endpoints import leaguedashplayerstats
from datetime import datetime
import time

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
#     NBA STATS LOGIC     #
# ======================= #

def get_season_leaders():
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season="2024-25",
        season_type_all_star="Regular Season"
    )
    players = stats.get_normalized_dict()["LeagueDashPlayerStats"]

    # Sort by Points Per Game (calculated manually)
    top_players = sorted(players, key=lambda x: x["PTS"] / x["GP"] if x["GP"] else 0, reverse=True)[:4]

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
        tweet += f"{rank} {name} ({team}): {ppg} PPG | {total_points} PTS\n\n"

    tweet += "#NBA #StatKingsHQ"
    return tweet


# ======================= #
#        MAIN BOT         #
# ======================= #

def run_bot():
    try:
        player_info = get_season_leaders()
        tweet = compose_tweet(player_info)

        print("Tweeting:\n", tweet)
        client.create_tweet(text=tweet)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    run_bot()
