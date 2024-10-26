from discord import slash_command, ApplicationContext
from discord.utils import get
from discord.ext import commands

from utils.data.mogi_manager import get_mogi, destroy_mogi
from models.MogiModel import Mogi

import asyncio


class leave_mogi(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.leave_semaphore = asyncio.Semaphore(1)

    @slash_command(name="leave", description="Leave this mogi")
    async def leave(self, ctx: ApplicationContext):
        async with self.leave_semaphore:
            mogi: Mogi = get_mogi(ctx.channel.id)
            if not mogi:
                return await ctx.respond("There is no mogi open in this channel.")
            if not [
                player for player in mogi.players if player.discord_id == ctx.author.id
            ]:
                return await ctx.respond("You're not in this mogi.")
            if mogi.isPlaying or mogi.isVoting:
                return await ctx.respond("This mogi has already started.")

            mogi.players = [
                player for player in mogi.players if player.discord_id != ctx.author.id
            ]
            await ctx.user.remove_roles(get(ctx.guild.roles, name="InMogi"))
            if len(mogi.players) == 0:
                destroy_mogi(ctx.channel.id)
                return await ctx.respond("# This mogi has been closed.")
            await ctx.respond(
                f"{ctx.author.mention} has left the mogi!\n{len(mogi.players)} players are in!"
            )


def setup(bot: commands.Bot):
    bot.add_cog(leave_mogi(bot))
