from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify
import discord
import random
import time

class pp(commands.Cog):
    """Penis related commands."""

    def __init__(self, bot):
        self.bot = bot
        default_config = {'king_dong': 134621854878007296}
        self._config = Config.get_conf(self, identifier=134621854878007300)
        self._config.register_global(**default_config)

    @commands.command()
    @checks.is_owner()
    async def set_king_dong(self, ctx, user: discord.Member):
        """Sets the king dong
    Totally not cheating because you rolled a 0 dick length."""

        await self._config.king_dong.set(user.id)

    @commands.command()
    async def pp(self, ctx, *users: discord.Member):
        """Detects user's penis length
        This is 100% accurate.
        Enter multiple users for an accurate comparison!"""
        
        msg = ""
        king_dong = await self._config.king_dong()
        
        if not users:
            users = (ctx.author,)
        
        for user in users:
            seed = hash(user.id + int(time.time()))
            random.seed(seed)
            
            if user.id == king_dong:
                dong_size = 40
            else:
                dong_size = random.randint(0, 30)

            msg += "**{}'s size:**\n8{}D\n".format(user.display_name, "=" * dong_size)


        for page in pagify(msg):
            await ctx.send(page)
    @commands.command()
    async def vag(self, ctx, *users: discord.Member):
        """Generates a random representation for vag.
        This is 100% not accurate.
        Enter multiple users for a fun comparison!"""
    
        msg = ""
        if not users:
            users = (ctx.author,)
    
        for user in users:
            seed = hash(user.id + int(time.time()))
            random.seed(seed)
    
            # Randomly generating each component of the representation
            width = random.choice([i for i in range(2, 11) if i % 2 == 0])
            flappage = random.choice([i for i in range(2, 11) if i % 2 == 0])
            stubble = random.randint(0, 1)
            clit = random.choice(["'", "•", "0"])
    
            # Constructing the vag representation
            flaps = '*'*(flappage//2)
            space = ' '*(width//2)
    
            vag = f"{':'*stubble}({flaps}{space}{clit}{space}{flaps}){':'*stubble}"
    
            msg += f"**{user.display_name}'s vag:**\n{vag}\n"
    
        for page in pagify(msg):
            await ctx.send(page)
