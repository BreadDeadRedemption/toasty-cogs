import discord
from redbot.core import commands

class RestrictedOwner(commands.Cog):
    """Manage your bot's owners and approved owners from within Discord!"""

    def __init__(self, bot):
        self.bot = bot
        self.owner = bot.owner
        self.approved_owners = {self.bot.owner_id}
        self.owner = self.bot.get_user(self.bot.owner_id)
        
    @commands.group(invoke_without_command=True)
    async def owner(self, ctx):
        """View bot owners and approved owners."""
        owners = []
        for owner_id in self.bot.owner_ids:
            owner = self.bot.get_user(owner_id)
            if owner:
                owners.append(f"{owner.name}#{owner.discriminator} (`{owner.id}`)")
        approved = []
        for owner_id in self.approved_owners:
            owner = self.bot.get_user(owner_id)
            if owner:
                approved.append(f"{owner.name}#{owner.discriminator} (`{owner.id}`)")
        embed = discord.Embed(
            title="Bot Owners and Approved Owners:",
            description=f"**Bot Owner:**\n{owners[0]}\n**Approved Owners:**\n{', '.join(approved) or 'None'}",
            color=await ctx.embed_color(),
        )
        await ctx.send(embed=embed)

    @owner.command()
    async def add(self, ctx, user: discord.User):
        """Add an approved owner."""
        if user.id in self.bot.owner_ids:
            return await ctx.send("That user is already one of the bot owners.")
        elif user.id in self.approved_owners:
            return await ctx.send("That user is already an approved owner.")
        else:
            self.approved_owners.add(user.id)
            await ctx.tick()
            await ctx.send(f"{user.mention} has been added as an approved owner.")

    @commands.command()
    async def ownreq(self, ctx, *, command):
        """Sends a request to the bot owner to approve a restricted command."""
        user = ctx.author
        if user.id not in self.approved_owners:
            return await ctx.send("You are not an approved owner.")
        else:
            owner = self.bot.owner
            if not owner:
                return await ctx.send("Bot owner not found.")
            msg = f"{user.mention} has requested permission for `{command}`. Approve? (y/n)"
            confirmation = await owner.send(msg)
            await confirmation.add_reaction("👍")
            await confirmation.add_reaction("👎")
            try:
                reaction, _ = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60.0,
                    check=lambda r, u: (
                        r.message.id == confirmation.id
                        and u.id == owner.id
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
