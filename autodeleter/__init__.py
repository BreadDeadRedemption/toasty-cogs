from .main import AutoDeleter

def setup(bot):
    bot.add_cog(AutoDeleter(bot))
