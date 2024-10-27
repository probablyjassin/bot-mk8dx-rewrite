from pymongo import UpdateOne

from models.MogiModel import Mogi
from utils.data.database import db_players


async def apply_mmr(mogi: Mogi) -> None:

    # we grab all_player_names from 'teams'
    # because 'teams' get shuffled
    # and mogi.mmr_resutls_by_group is in the same order as 'teams'
    all_player_names = [player.name for team in mogi.teams for player in team]
    all_player_mmrs = [player.mmr for team in mogi.teams for player in team]
    all_player_new_mmrs = [
        all_player_mmrs[i] + mogi.mmr_results_by_group[i]
        for i in range(0, len(mogi.players))
    ]

    # create objects to update in the database in bulk
    data_to_update_obj = [
        {
            "name": all_player_names[i],
            "new_mmr": all_player_new_mmrs[i],
            "delta": mogi.mmr_results_by_group[i],
        }
        # don't update subs unless they gained mmr
        for i in range(len(all_player_names))
        if not any(sub.name == all_player_names[i] for sub in mogi.subs)
        or mogi.mmr_results_by_group[i] > 0
    ]

    db_players.bulk_write(
        [
            UpdateOne(
                {"name": entry["name"]},
                {
                    "$set": {"mmr": entry["new_mmr"] if entry["new_mmr"] > 0 else 1},
                    "$push": {"history": entry["delta"]},
                },
                upsert=False,
            )
            for entry in data_to_update_obj
        ]
    )
