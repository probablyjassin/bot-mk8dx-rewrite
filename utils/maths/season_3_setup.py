import os
import sys
import json
import math
from bson.int64 import Int64

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from models.RankModel import Rank

season_2_json = []
season_3_json = []

skips = {
    "mmr": 0,
    "history": 0,
}

if len(sys.argv) != 2:
    print("Usage: python season_3_setup <filename>")
    sys.exit(1)

filename = sys.argv[1]

all_ranks = list(Rank.__members__.values())
rank_name_to_rank = {rank.rankname: rank for rank in all_ranks}

if not os.path.exists(filename):
    print(f"Error: File '{filename}' not found")
    sys.exit(1)

with open(filename, "r", encoding="utf-8") as file:
    season_2_json = json.load(file)
    print(f"Loaded {len(season_2_json)} entries")

    print("Matching data to new season structure...")
    s2_player: dict
    for s2_player in season_2_json:
        if s2_player.get("mmr") == 2000:
            print(f"Skipping player '{s2_player.get('name')}' with default MMR")
            skips["mmr"] += 1
            continue
        if not len(s2_player.get("history")):
            print(f"Skipping player '{s2_player.get('name')}' no mogis played")
            skips["history"] += 1
            continue

        s2_player_rank = Rank.getRankByMMR(s2_player.get("mmr"))

        rank_index = list(rank_name_to_rank.keys()).index(s2_player_rank.rankname)
        s3_player_rank = all_ranks[max(rank_index - 1, 0)]
        new_mmr = max(s3_player_rank.mmrrange[0], 2500)

        s2_mmr_rounded = int(math.floor(s2_player.get("mmr") / 100)) * 100

        s3_player_mmr = s2_mmr_rounded if s2_player.get("mmr") < new_mmr else new_mmr

        s3_player = {
            "name": s2_player.get("name"),
            "discord_id": Int64(s2_player.get("discord")),
            "mmr": max(s3_player_mmr, 2000),
            "history": [],
        }
        if s2_player.get("dc"):
            s3_player["disconnects"] = s2_player.get("dc")
        if s2_player.get("joined"):
            s3_player["joined"] = s2_player.get("joined")
        if s2_player.get("inactive"):
            s3_player["inactive"] = True
        if s2_player.get("suspended"):
            s3_player["suspended"] = True
        season_3_json.append(s3_player)

print("Writing to OUT_season_3.json...")
with open("test-OUT_season_3.json", "w", encoding="utf-8") as file:
    file.write(json.dumps(season_3_json, indent=4, ensure_ascii=False))

print(
    "----------------------------------------\n"
    f"Original entries: {len(season_2_json)}\n"
    f"Wrote {len(season_3_json)} entries"
    f" ({len(season_2_json) - len(season_3_json)} skipped)\n"
    f"Skipped because still at 2000 MMR: {skips['mmr']}\n"
    f"Skipped because no mogis played in season 2: {skips['history']}\n"
    "----------------------------------------\n"
)

print("Done")
