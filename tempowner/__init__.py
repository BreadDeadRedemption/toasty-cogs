from .main import TempOwner


def setup(bot):
    bot.add_cog(TempOwner(bot))
