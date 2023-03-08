import discord
from redbot.core import commands

class OwnerManagement(commands.Cog):
    """Manage your bot's owners and approved owners from within Discord!"""

    __author__ = ["JeffJrShim"]
    __version__ = "1.2.0"

    def __init__(self, bot):
        self.bot = bot
        self.default_owners = self.bot.owner_ids.copy()
        self.approved_owners = set()

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad!"""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nAuthors: {', '.join(self.__author__)}\nCog Version: {self.__version__}"

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def owner(self, ctx):
        """Owner management commands"""
        if ctx.invoked_subcommand is None:
            owners = ""
            for _id in list(self.bot.owner_ids):
                owner = self.bot.get_user(_id)
                owners += f"- {owner} (`{owner.id}`)\n"
            approved = ""
            for _id in list(self.approved_owners):
                owner = self.bot.get_user(_id)
                approved += f"- {owner} (`{owner.id}`)\n"
            embed = discord.Embed(
                title="Bot Owners and Approved Owners:",
                description=f"**Bot Owners:**\n{owners}\n**Approved Owners:**\n{approved}",
                color=await ctx.embed_color(),
            )
            await ctx.send(embed=embed)

    @owner.command(invoke_without_command=True)
    @commands.is_owner()
    async def add(self, ctx, *, user: discord.User):
        """Add an approved owner. This user will be able to send restricted commands that require owner approval."""
        user = self.bot.get_user(user.id)
        if user.id in self.bot.owner_ids:
            return await ctx.send("That user is already one of the bot owners.")
        elif user.id in self.approved_owners:
            return await ctx.send("That user is already an approved owner.")
        else:
            self.approved_owners.add(user.id)
            await ctx.tick()
            await ctx.send(f"{user} has been added as an approved owner.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def ownerrequest(self, ctx, *, command):
        """Sends a request to the bot owner to approve a restricted command."""
        print(f"Received owner request from {ctx.author} for command '{command}'.")
        user = ctx.author
        if user.id not in self.approved_owners:
            return await ctx.send("You are not an approved owner.")
        else:
            owner_names = [str(self.bot.get_user(owner_id)) for owner_id in self.bot.owner_ids]
            owner_mentions = " ".join(f"<@{owner_id}>" for owner_id in self.bot.owner_ids)
            msg = f"{user} has requested permission for `{command}`. Approve? (y/n)"
            confirmation = await ctx.send(f"{owner_mentions} {msg}")
            await confirmation.add_reaction("👍")
            await confirmation.add_reaction("👎")
            try:
                reaction, _ = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60.0,
                    check=lambda r, u: (
                        r.message.id == confirmation.id
                        and u.id in self.bot.owner_ids
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
