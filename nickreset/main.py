import discord
from redbot.core import commands


class MassUnnick(commands.Cog):
    """Unnick all members of the server."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def unnickall(self, ctx):
        """Unnick all members of the server."""

        embed = discord.Embed(
            title=f"Starting... 🔃", description="Initiating mass unnick", color=0x000000
        )
        message = await ctx.send(embed=embed)

        amount = 0

        async for member in ctx.guild.fetch_members(limit=None):
            amount += 1

            try:
                await member.edit(nick=None)
            except (discord.Forbidden, discord.HTTPException) as error:
                amount -= 1

                embed = discord.Embed(
                    title=f"Error {error}",
                    description=f"With User: {member.name}#{member.discriminator}",
                    color=0x000000,
                )
                await message.edit(embed=embed)
                continue

        embed = discord.Embed(
            title=f"Success! ✅",
            description=f"Unnicked {amount} of users!",
            color=0x000000,
        )
        await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(MassUnnick(bot))
