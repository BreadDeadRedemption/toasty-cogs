
from .main import RestrictedOwner

def setup(bot):
    bot.add_cog(RestrictedOwner(bot))
