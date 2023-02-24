from redbot.core import commands
from .threadfiltercog import ThreadFilterCog

def setup(bot):
    cog = ThreadFilterCog(bot)
    bot.add_cog(cog)
