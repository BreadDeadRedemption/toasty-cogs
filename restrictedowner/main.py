import discord
from redbot.core import commands

class RestrictedOwner(commands.Cog):
    """Manage your bot's owners and approved owners from within Discord!"""

    def __init__(self, bot):
        self.bot = bot
        self.approved_owners = set()

        
    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def owner(self, ctx):
        """Owner management commands"""
        if ctx.invoked_subcommand is None:
            owners = ""
            for _id in self.bot.owner_ids:
                owner = self.bot.get_user(_id)
                owners += f"- {owner} (`{owner.id}`)\n"
            approved = ""
            for _id in self.approved_owners:
                owner = self.bot.get_user(_id)
                approved += f"- {owner} (`{owner.id}`)\n"
            embed = discord.Embed(
                title="Bot Owners and Approved Owners:",
                description=f"**Bot Owner:**\n{self.bot.owner_id[0]}\n**Approved Owners:**\n{approved}",
                color=await ctx.embed_color(),
            )
            await ctx.send(embed=embed)


    @owner.command(invoke_without_command=True)
    @commands.is_owner()
    async def add(self, ctx, *, user: discord.User):
        """Add an approved owner. This user will be able to send restricted commands that require owner approval."""
        user = self.bot.get_user(user.id)
        if user.id in self.approved_owners:
            return await ctx.send("That user is already an approved owner.")
        else:
            self.approved_owners.add(user.id)
            await ctx.tick()
            await ctx.send(f"{user} has been added as an approved owner.")

    @commands.command(hidden=True)
    async def ownerrequest(self, ctx, *, command):
        """Sends a request to the bot owner to approve a restricted command."""
        user = ctx.author
        if user.id not in self.approved_owners:
            return await ctx.send("You are not an approved owner.")
        else:
            owner = await self.bot.fetch_user(self.bot.owner_id)
            msg = f"{user} has requested permission for `{command}`. Approve? (y/n)"
            dm_channel = await owner.create_dm()
            dm_message = await dm_channel.send(msg)
            await dm_message.add_reaction("👍")
            await dm_message.add_reaction("👎")
            try:
                reaction, _ = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60.0,
                    check=lambda r, u: (
                        r.message.id == dm_message.id
                        and u.id == self.bot.owner_id
                        and str(r.emoji) in ["👍", "👎"]
                    ),
                )
            except asyncio.TimeoutError:
                await dm_channel.send("Request timed out. Try again later.")
                return
            if str(reaction.emoji) == "👍":
                await dm_channel.send("Request approved. Running command...")
                await self.bot.process_commands(ctx.message)
            else:
                await dm_channel.send("Request denied. Command not run.")
