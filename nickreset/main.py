import discord
from redbot.core import commands
import json

class MassUnnick(commands.Cog):
    """Mass unnick command."""

    def __init__(self, bot):
        self.bot = bot
        self.config = json.loads(bot.db.config.get_raw("UnnickAll", {}))
        self.excluded_roles = set(self.config.get("excluded_roles", []))

    @commands.group()
    async def unnickall(self, ctx):
        """Unnick all members in the guild."""
        pass

    @unnickall.command()
    @commands.has_permissions(manage_nicknames=True)
    async def start(self, ctx):
        """Starts unnicking all members in the guild."""
        embed = discord.Embed(title=f"Starting... 🔃", description="Initiating mass unnick", color=0x000000)
        message = await ctx.send(embed=embed)
        amount = 0

        for member in ctx.guild.members:
            if self._is_excluded(member):
                continue
            try:
                await member.edit(nick=None)
                amount += 1
            except (discord.Forbidden, discord.HTTPException) as error:
                embed = discord.Embed(title=f"Error {error}", description=f"With User: {member.name}#{member.discriminator}", color=0x000000)
                await ctx.send(embed=embed)
                continue

        embed = discord.Embed(title=f"Success! ✅", description=f"Unnicked {amount} of users!", color=0x000000)
        await message.edit(embed=embed)

    @unnickall.command()
    @commands.has_permissions(manage_nicknames=True)
    async def exclude(self, ctx, *roles: discord.Role):
        """Exclude specified roles from being unnicked."""
        self.excluded_roles |= set(role.id for role in roles)
        self.config["excluded_roles"] = list(self.excluded_roles)
        await self.bot.db.config.update_raw("UnnickAll", self.config)
        await ctx.send("Roles excluded successfully.")

    def _is_excluded(self, member):
        return any(role.id in self.excluded_roles for role in member.roles)
