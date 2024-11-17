from discord.ext import commands
from bson.int64 import Int64

from utils.data.database import db_players
from models.CustomMogiContext import MogiApplicationContext
from models.RankModel import Rank

from discord import slash_command


class season3(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @slash_command(name="season3")
    async def season3(self, ctx: MogiApplicationContext):
        await ctx.response.defer()

        registered_not_in_server = []

        lounge_player_role = ctx.get_lounge_role("Lounge Player")
        rank_roles = [
            ctx.get_lounge_role(f"Lounge - {name}")
            for name in ["Wood", "Bronze", "Silver", "Gold", "Platinum", "Diamond"]
        ]

        all_players = list(db_players.find({}))

        for discord_member in ctx.get_lounge_role("Lounge Player").members:
            if not any(
                player["discord_id"] == discord_member.id for player in all_players
            ):
                await ctx.send(
                    f"Could not find {discord_member.display_name} with id {discord_member.id} in the database"
                )
                continue
        for role in rank_roles:
            for member in role.members:
                if lounge_player_role not in member.roles:
                    await ctx.send(
                        f"{member.display_name}({member.id}) has {role.name} but not Lounge Player"
                    )

        for player in all_players:
            try:
                discord_user = await ctx.guild.fetch_member(player["discord_id"])
            except:
                discord_user = None
            if not discord_user:
                await ctx.send(
                    f"Could not find {player['name']} with id {player['discord_id']} on the discord server"
                )
                registered_not_in_server.append(player["discord_id"])
                continue
            if lounge_player_role not in discord_user.roles:
                await ctx.send(
                    f"{discord_user.display_name} doesn't have the Lounge Player Role"
                )
            player_rank = Rank.getRankByMMR(player["mmr"])
            if ctx.get_lounge_role(f"Lounge - {player_rank}") not in discord_user.roles:
                await discord_user.add_roles(
                    ctx.get_lounge_role(f"Lounge - {player_rank}")
                )
                await ctx.send(
                    f"Added {ctx.get_lounge_role(f'Lounge - {player_rank}').name} to {discord_user.display_name}"
                )
            for role in rank_roles:
                if (
                    role != ctx.get_lounge_role(f"Lounge - {player_rank}")
                    and role in discord_user.roles
                ):
                    await discord_user.remove_roles(role)
                    await ctx.send(
                        f"Removed {role.name} from {discord_user.display_name}"
                    )

        await ctx.respond(f"{registered_not_in_server}")

    @slash_command(name="season3_2")
    async def season3_2(self, ctx: MogiApplicationContext):
        await ctx.response.defer()
        registered_not_on_server = [
            797496504100454460,
            400658926695088138,
            911636359675006989,
            701477012698562671,
            1110433045821001750,
            924870906382254080,
            632478120372469761,
            917502484187086848,
            578525627401895936,
            219460037901418496,
            1259020282249609267,
            602566137145851914,
            435860262621282305,
            492362658071183370,
            661301445584486421,
            1260428957141045262,
            191561486710079488,
            731814803349438504,
            1168732610936176710,
        ]
        for user_id in registered_not_on_server:
            await ctx.send(f"{user_id} not on the server, removing from database")
            db_players.delete_one({"discord_id": Int64(user_id)})

        await ctx.respond("Done")

    @slash_command(name="season3_unset_dc")
    async def season3_unset_dc(self, ctx: MogiApplicationContext):
        await ctx.response.defer()
        db_players.update_many({}, {"$set": {"disconnects": None}})
        await ctx.respond("Done")


def setup(bot: commands.Bot):
    bot.add_cog(season3(bot))
