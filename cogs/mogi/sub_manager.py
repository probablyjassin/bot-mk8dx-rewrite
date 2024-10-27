from discord import SlashCommandGroup, Option, ApplicationContext
from discord.ext import commands

from models.PlayerModel import PlayerProfile
from models.MogiModel import Mogi

from utils.command_helpers.valid_discord_mention import is_discord_mention
from utils.data.mogi_manager import get_mogi
from utils.data.database import db_players
from utils.command_helpers.checks import is_mogi_open, is_mogi_in_progress


def replace(space, player, sub):
    if isinstance(space, list):
        return [replace(item, player, sub) for item in space]
    else:
        return sub if space == player else space


class sub_manager(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    replacement = SlashCommandGroup(
        name="replacement", description="Substitute a player"
    )

    @replacement.command(name="sub")
    @is_mogi_open()
    @is_mogi_in_progress()
    async def sub(
        self,
        ctx: ApplicationContext,
        player_name: str = Option(
            str, name="player", description="Player that needs a sub."
        ),
        replacement_name: str = Option(
            str, name="sub", description="Replacement player coming in."
        ),
    ):
        mogi: Mogi = get_mogi(ctx.channel.id)

        # user can input both discord mention or player name
        # check for both cases
        if (
            not is_discord_mention(player_name)
            and player_name not in [player.name for player in mogi.players]
        ) or (
            is_discord_mention(player_name)
            and int(player_name.strip("<@>"))
            not in [player.discord_id for player in mogi.players]
        ):
            return await ctx.respond("Player not in the mogi", ephemeral=True)

        if (
            is_discord_mention(player_name)
            and player_name in [player.name for player in mogi.players]
        ) or (
            not is_discord_mention(player_name) and int(player_name.strip("<@>"))
            if is_discord_mention(player_name)
            else None in [player.discord_id for player in mogi.players]
        ):
            return await ctx.respond("Sub is already in the mogi.", ephemeral=True)

        player_profile = [
            player for player in mogi.players if player.name == player_name
        ][0]

        replacement_profile = PlayerProfile(
            **db_players.find_one(
                {
                    "$or": [
                        {"name": replacement_name},
                        {
                            "discord_id": (
                                int(replacement_name.strip("<@>"))
                                if is_discord_mention(replacement_name)
                                else None
                            )
                        },
                    ]
                }
            )
        )
        if not replacement_profile:
            return await ctx.respond(
                "The sub does not have a Lounge Profile", ephemeral=True
            )

        mogi.players = replace(mogi.players, player_profile, replacement_profile)
        mogi.teams = replace(mogi.teams, player_profile, replacement_profile)

        mogi.subs.append(replacement_profile)

        await ctx.respond(
            f"<@{player_profile.discord_id}> has been subbed out for <@{replacement_profile.discord_id}>"
        )

    @replacement.command(name="unsub")
    async def sub(self, ctx: ApplicationContext):
        pass


def setup(bot: commands.Bot):
    bot.add_cog(sub_manager(bot))
