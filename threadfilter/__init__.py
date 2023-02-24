from .main import ThreadFilterCog

def setup(bot):
    bot.add_cog(ThreadFilterCog(bot))
