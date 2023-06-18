from .acrophobia import Acrophobia

async def setup(bot):
    await bot.add_cog(Acrophobia(bot))
