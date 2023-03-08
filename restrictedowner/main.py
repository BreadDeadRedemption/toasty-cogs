from redbot.core import commands
import discord

class RestrictedOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.approved_partners = {bot.owner_id}

    @commands.command()
    async def partner(self, ctx):
        """Displays the bot owner's name and discriminator, as well as a list of all approved partners."""
        owner = self.bot.get_user(self.bot.owner_id)
        partner_list = '\n'.join([str(self.bot.get_user(partner_id)) for partner_id in self.approved_partners])
        await ctx.send(f"Bot owner: {owner.name}#{owner.discriminator}\nApproved partners:\n{partner_list}")

    @commands.group()
    async def partner(self, ctx):
        """Allows the bot owner to manage approved partners."""
        pass

    @partner.command()
    async def add(self, ctx, user: discord.User):
        """Adds an approved partner."""
        if user.id == self.bot.owner_id or user.id in self.approved_partners:
            await ctx.send("This user is already an approved partner or the bot owner.")
        else:
            self.approved_partners.add(user.id)
            await ctx.send(f"{user.name}#{user.discriminator} has been added as an approved partner.")

    @commands.command()
    async def partreq(self, ctx, command: str):
        """Sends a request to the bot owner to approve a restricted command."""
        if ctx.author.id not in self.approved_partners:
            await ctx.send("You are not an approved partner.")
            return
        
        await ctx.send("Request sent. Waiting for bot owner's approval...")
        owner = self.bot.get_user(self.bot.owner_id)
        message = await owner.send(f"{ctx.author.name}#{ctx.author.discriminator} has requested permission to run the command: `{command}`. React with 👍 to approve or 👎 to deny.")
        await message.add_reaction('👍')
        await message.add_reaction('👎')

        def check(reaction, user):
            return user == owner and (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎')

        reaction, _ = await self.bot.wait_for('reaction_add', check=check)

        if str(reaction.emoji) == '👍':
            await ctx.send("Approval granted. Running command...")
            await ctx.invoke(self.bot.get_command(command))
        else:
            await ctx.send("Approval denied.")
            
        await ctx.author.send("Your request to run the command has been processed.")
