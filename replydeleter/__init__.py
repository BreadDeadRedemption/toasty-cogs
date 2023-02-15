from .main import ReplyDeleter

def setup(bot):
    bot.add_cog(ReplyDeleter(bot))
