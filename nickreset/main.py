import discord
from redbot.core import commands

class MassUnnick(commands.Cog):
    """Unnick all members in the server"""

    def __init__(self, bot):
        self.bot = bot
        self.excluded_roles = []  # a list of role IDs to exclude from unnicking

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def unnickall(self, ctx):
        """Remove all nicknames from members in the server"""
        amount = 0
        for member in ctx.guild.members:
            # Check if member has an excluded role
            excluded = False
            for role in member.roles:
                if role.id in self.excluded_roles:
                    excluded = True
                    break
            if excluded:
                continue
            try:
                await member.edit(nick=None)
                amount += 1
            except discord.Forbidden:
                pass
        await ctx.send(f"Unnicked {amount} members.")

    @unnickall.command(name="exclude")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def unnickall_exclude(self, ctx, role: discord.Role):
        """Exclude a role from being unnicked"""
        if role.id in self.excluded_roles:
            await ctx.send(f"{role.name} is already excluded.")
        else:
            self.excluded_roles.append(role.id)
            await ctx.send(f"{role.name} added to excluded roles.")

    @unnickall.command(name="unexclude")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def unnickall_unexclude(self, ctx, role: discord.Role):
        """Remove a role from the excluded list"""
        if role.id in self.excluded_roles:
            self.excluded_roles.remove(role.id)
            await ctx.send(f"{role.name} removed from excluded roles.")
        else:
            await ctx.send(f"{role.name} is not in excluded roles.")
