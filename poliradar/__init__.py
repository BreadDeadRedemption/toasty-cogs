from .main import RadarCog


def setup(bot):
    bot.add_cog(RadarCog(bot))
