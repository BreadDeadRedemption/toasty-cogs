import discord
from redbot.core import commands

class RestrictedOwner(commands.Cog):
    """Manage your bot's partners and approved partners from within Discord!"""

    def __init__(self, bot):
        self.bot = bot
        self.approved_partners = {self.bot.owner_id}
        
    @commands.group(invoke_without_command=True)
    async def partner(self, ctx):
        """View bot owner and approved partners."""
        partners = [f"{self.bot.owner.name}#{self.bot.owner.discriminator} (`{self.bot.owner.id}`)"]
        approved = []
        for partner_id in self.approved_partners:
            partner = self.bot.get_user(partner_id)
            if partner:
                approved.append(f"{partner.name}#{partner.discriminator} (`{partner.id}`)")
        embed = discord.Embed(
            title="Bot Owner and Approved Partners:",
            description=f"**Bot Owner:**\n{partners[0]}\n**Approved Partners:**\n{', '.join(approved) or 'None'}",
            color=await ctx.embed_color(),
        )
        await ctx.send(embed=embed)

    @partner.command()
    async def add(self, ctx, user: discord.User):
        """Add an approved partner."""
        if user.id in self.bot.owner_ids:
            return await ctx.send("That user is already the bot owner.")
        elif user.id in self.approved_partners:
            return await ctx.send("That user is already an approved partner.")
        else:
            self.approved_partners.add(user.id)
            await ctx.tick()
            await ctx.send(f"{user.mention} has been added as an approved partner.")

    @commands.command()
    async def partreq(self, ctx, *, command):
        """Sends a request to the bot owner to approve a restricted command."""
        user = ctx.author
        if user.id not in self.approved_partners:
            return await ctx.send("You are not an approved partner.")
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
