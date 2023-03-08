import discord
from redbot.core import commands
import asyncio

class RestrictedOwner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.approved_owners = set()

    @commands.group(invoke_without_command=True)
    async def owner(self, ctx):
        """Owner management commands"""
        if ctx.invoked_subcommand is None:
            approved = ""
            for _id in list(self.approved_owners):
                owner = self.bot.get_user(_id)
                approved += f"- {owner} (`{owner.id}`)\n"
            embed = discord.Embed(
                title="Bot Owners and Approved Owners:",
                description=f"**Bot Owner:**\n{self.bot.owner_id}\n**Approved Owners:**\n{approved}",
                color=await ctx.embed_color(),
            )
            await ctx.send(embed=embed)

    @owner.command(invoke_without_command=True)
    async def add(self, ctx, *, user: discord.User):
        """Add an approved owner. This user will be able to send restricted commands that require owner approval."""
        user = self.bot.get_user(user.id)
        if user.id == self.bot.owner_id:
            return await ctx.send("That user is already the bot owner.")
        elif user.id in self.approved_owners:
            return await ctx.send("That user is already an approved owner.")
        else:
            self.approved_owners.add(user.id)
            await ctx.tick()
            await ctx.send(f"{user} has been added as an approved owner.")

    @commands.command(hidden=True, name="ownreq")
    async def owner_request(self, ctx, *, command):
        """Sends a request to the bot owner to approve a restricted command."""
        user = ctx.author
        if user.id not in self.approved_owners:
            return await ctx.send("You are not an approved owner.")
        else:
            owner = self.bot.get_user(self.bot.owner_id)
            msg = f"{user} has requested permission for `{command}`. Approve? (y/n)"
            confirmation = await owner.send(msg)
            await confirmation.add_reaction("👍")
            await confirmation.add_reaction("👎")
            print("Owner request sent.")
            try:
                reaction, _ = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60.0,
                    check=lambda r, u: (
                        r.message.id == confirmation.id
                        and u.id == self.bot.owner_id
                        and str(r.emoji) in ["👍", "👎"]
                    ),
                )
            except asyncio.TimeoutError:
                return await ctx.send("Request timed out. Try again later.")
            if str(reaction.emoji) == "👍":
                await ctx.send("Request approved. Running command...")
                await self.bot.process_commands(ctx.message)
            else:
                await ctx.send("Request denied. Command not run.")
