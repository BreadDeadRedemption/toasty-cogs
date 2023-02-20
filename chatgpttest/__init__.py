from .cog import ChatGPTCog

def setup(bot):
bot.add_cog(ChatGPT(bot))
