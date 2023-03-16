import discord
from redbot.core import commands
from typing import Dict
from asyncio import TimeoutError

class TempOwner(commands.Cog):
    """Temporary bot owner management cog."""

    __author__ = ["Your Name"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot
        self.semiowners: Dict[int, int] = {}

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def owner(self, ctx):
        """Owner management commands."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @owner.command(name="add")
    @commands.is_owner()
    async def add_semiowner(self, ctx, *, user: discord.User):
        """Add a semi-owner."""
        if user.id in self.semiowners:
            await ctx.send(f"{user} is already a semi-owner.")
        else:
            self.semiowners[user.id] = ctx.guild.id
            await ctx.send(f"{user} has been added as a semi-owner.")

    async def temp_owner_check(self, ctx):
        is_owner = await self.bot.is_owner(ctx.author)
        is_semiowner = ctx.author.id in self.semiowners and self.semiowners[ctx.author.id] == ctx.guild.id

        if is_owner or is_semiowner:
            return True
        else:
            await ctx.send("This is a bot owner only command, send request? (y/n)")
            try:
                response = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
                if response.content.lower() == 'y':
                    owner = (await self.bot.application_info()).owner
                    dm_channel = owner.dm_channel or await owner.create_dm()

                    def check(m):
                        return m.author == owner and m.channel == dm_channel

                    await dm_channel.send(f"{ctx.author} in {ctx.guild.name} has requested to run the following command: `{ctx.message.content}` Approve?\n\na | Yes only approve it once\nb | No\nc <minutes> | Yes and grant them unrestricted access for _ minutes\nd <minutes> | Yes and give them access to this one command for _ minutes")

                    try:
                        approval = await self.bot.wait_for('message', check=check, timeout=60)

                        if approval.content.lower().startswith("a"):
                            return True
                        elif approval.content.lower().startswith("b"):
                            await ctx.send("Request denied.")
                        elif approval.content.lower().startswith("c"):
                            _, minutes = approval.content.split(" ")
                            minutes = int(minutes)
                            self.semiowners[ctx.author.id] = ctx.guild.id
                            await asyncio.sleep(minutes * 60)
                            del self.semiowners[ctx.author.id]
                        elif approval.content.lower().startswith("d"):
                            _, minutes = approval.content.split(" ")
                            minutes = int(minutes)
                            await asyncio.sleep(minutes * 60)
                            return True
                    except TimeoutError:
                        await ctx.send("Approval request timed out.")
                else:
                    await ctx.send("Request not sent.")
            except TimeoutError:
                await ctx.send("No response given.")
return False

    def setup(bot):
    temp_owner_management_cog = TempOwner(bot)
    async def temp_owner_or_is_owner(ctx):
        return await temp_owner_management_cog.temp_owner_check(ctx)

    bot.add_cog(temp_owner_management_cog)
    bot.add_check(temp_owner_or_is_owner)

