from redbot.core.utils import get_end_user_data_statement

from .main import DisboardReminder

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)


async def setup(bot):
    cog = DisboardReminder(bot)
    bot.add_cog(cog)
