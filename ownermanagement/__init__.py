from .main import OwnerManagement


def setup(bot):
    bot.add_cog(OwnerManagement(bot))
