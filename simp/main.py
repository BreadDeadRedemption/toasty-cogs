from __future__ import annotations
import random
from typing import cast
import asyncio
import os
import discord
from discord.ext import commands
from redbot.core import checks, commands
from redbot.core.bot import Red
from .database import SimpUser


class SimpTracker(commands.Cog):
    SIMP_USER_LIMIT = 3

    def __init__(self, bot: Red):
        self.bot = bot

    @commands.command(
        name="simp",
        brief="Add a person that you're simping for.",
    )
    async def add_simp(self, ctx: commands.Context, user: discord.Member) -> None:
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

    @commands.command(
        name="unsimp",
        brief="Stop simping for a person.",
    )
    async def remove_simp(self, ctx: commands.Context) -> None:
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
            f"Which user do you want to stop simping for?",
        
            view=discord.ui.View(select),
        )
        select.message = message

        # Wait for user to select
        try:
            await select.interaction.wait(timeout=15.0)
        except asyncio.TimeoutError:
            await message.edit(content="Timed out.", view=None)
            return

        # Remove from database
        selected_user_id = int(select.values[0])
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

    @commands.command(
        name="simps",
        brief="Show who you're simping for.",
    )
    async def list_simps(self, ctx: commands.Context) -> None:
        """
        Show who a user is simping for.
        """

        # Get their current simp list
        current_simping = await SimpUser.fetch(
            guild_id=ctx.guild.id,
            user_id=ctx.author.id,
        )
        if not current_simping:
            return await ctx.send("You are not simping for anyone at the moment.")
        simp_list = [
            f"{ctx.guild.get_member(s.simping_for).mention}"
            for s in current_simping
        ]
        await ctx.send(
            f"You are simping for: {', '.join(simp_list)}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.command(
        name="simpstats",
        brief="Display simping stats for a user.",
    )
    async def stats(self, ctx: commands.Context, user: discord.Member = None) -> None:
        """
        Display a user's simping stats.
        """

        if user is None:
            user = ctx.author

        # Get their simps and who they are simping for
        user_simps = await SimpUser.fetch(
            guild_id=ctx.guild.id,
            user_id=user.id,
        )
        if not user_simps:
            return await ctx.send(
                f"{user.display_name} is not currently being simped for by anyone.",
            )

        simping_for = [ctx.guild.get_member(s.simping_for) for s in user_simps]

        # Display results
        embed = discord.Embed(title=f"Simp stats for {user.display_name}")
        embed.add_field(
            name="Number of simps:",
            value=len(user_simps),
            inline=True,
        )
        embed.add_field(
            name="Simping for:",
            value="\n".join([u.mention for u in simping_for]),
            inline=True,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="simprank",
        brief="Display a leaderboard of top simps.",
    )
    async def leaderboard(self, ctx: commands.Context) -> None:
        """
        Display the top simps in the server.
        """

        all_simps = await SimpUser.all()

        # Group by user
        user_groups = {}
        for simp in all_simps:
            if simp.user_id not in user_groups:
                user_groups[simp.user_id] = []
            user_groups[simp.user_id].append(simp.simping_for)

        # Sort by number of simps
        sorted_users = sorted(user_groups.items(), key=lambda x: len(x[1]), reverse=True)

        # Display results
        embed = discord.Embed(title="Simp Leaderboard", color=0xff)
        embed.set_thumbnail(url="https://i.imgur.com/PvpfiRs.png")
        if not sorted_users:
            return await ctx.send("No one is simping for anyone in this server.")
        for i, (user_id, simping_for) in enumerate(sorted_users[:10]):
            user = ctx.guild.get_member(user_id)
            if not user:
                continue
            embed.add_field(
                name=f"{i+1}. {user.display_name}",
                value=f"Simping for: {len(simping_for)}",
                inline=True,
            )
        await ctx.send(embed=embed)


