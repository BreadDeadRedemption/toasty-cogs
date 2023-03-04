from typing import cast
import asyncio
import os
import discord
from discord.ext import commands
from redbot.core import checks
from redbot.core import commands as red_commands
from redbot.core.bot import Red
from .database import SimpUser


class SimpTracker(red_commands.Cog):
    SIMP_USER_LIMIT = 3

    def __init__(self, bot: Red):
        self.bot = bot

    @red_commands.command(
        name="simp",
        brief="Add a person that you're simping for.",
    )
    async def add_simp(self, ctx: red_commands.Context, user: discord.Member) -> None:
        """
        Allow a user to simp for another user.
        """

        # Disable yourself
        if ctx.author == user:
            return await ctx.send(
                "There's \"self love\" and then there's whatever _this_ is :/",
            )

        # See if they're already simping for that user.
        current_simping = await SimpUser.fetch(
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
        )
        if [i for i in current_simping if i.simping_for == user.id]:
            return await ctx.send(
                (
                    "This is very sweet and all, but {0}, you're _already_ "
                    "simping for {1} :/"
                ).format(ctx.author.mention, user.mention),
            )

        # Get their current simp count
        if (current := len(current_simping)) >= self.SIMP_USER_LIMIT:
            return await ctx.send(
                (
                    "Sorry, {0}, you're already simping for **{1}** people - "
                    "you have hit the simp user limit."
                ).format(ctx.author.mention, current),
            )

        # Add to database
        await SimpUser.create(
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
            simping_for=user.id,
        )
        await ctx.send(
            f"You are now simping for **{user.mention}**!",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @red_commands.command(
        name="unsimp",
        brief="Stop simping for a person.",
    )
    async def remove_simp(self, ctx: red_commands.Context) -> None:
        """
        Allow a user to stop simping for another user.
        """

        # See if they're already simping for anyone.
        current_simping = await SimpUser.fetch(
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
        )
        if not current_simping:
            return await ctx.send("You are not simping for anyone at the moment.")

        requested_users = await ctx.guild.fetch_members(
            *[i.simping_for for i in current_simping],
        )
        users: dict[int, discord.Member] = {}
        for ru in requested_users:
            users[ru.id] = ru

        # Send select menu for user to remove
        options = [
            discord.SelectOption(
                label=str(users[i.simping_for]),
                value=str(i.simping_for),
            )
            for i in current_simping
        ]
        select = discord.ui.Select(
            options=options,
            placeholder="Which user do you want to stop simping for?",
            min_values=1,
            max_values=1,
        )
        message = await ctx.send(
            f"Which user do you want to stop simping for?",)
        select = discord.ui.Select(
            options=options,
            placeholder="Which user do you want to stop simping for?",
            min_values=1,
            max_values=1,
        )
        view = discord.ui.View()
        view.add_item(select)
        message = await ctx.send(
            f"Which user do you want to stop simping for?",
            view=view,
        )

        # Wait for user to select
        try:
            interaction = await self.bot.wait_for(
                "select_option", timeout=15.0, check=lambda i: i.custom_id == select.custom_id
            )
        except asyncio.TimeoutError:
            await message.edit(content="Timed out.", view=None)
            return

        selected_user_id = int(interaction.values[0])
        await SimpUser.filter(
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
            simping_for=selected_user_id,
        ).delete()

        # Send confirmation
        selected_user = cast(discord.Member, ctx.guild.get_member(selected_user_id))
        await message.edit(
            content=f"You have stopped simping for **{selected_user.mention}**.",
            view=None,
        )

