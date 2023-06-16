from .properpp import pp

async def setup(bot):
    await bot.add_cog(pp(bot))
