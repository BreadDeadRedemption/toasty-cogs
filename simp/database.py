from redbot.core import Config, checks, commands
import asyncpg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redbot.core.bot import Red

import utils.database


class Database(commands.Cog):
    """Database management cog."""

    def __init__(self, bot: "Red"):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=123456789)

    async def initialize(self) -> None:
        if not await self.config.database_dsn():
            raise ValueError("Missing database DSN from config.")
        try:
            utils.database.pool = await asyncpg.create_pool(await self.config.database_dsn())
        except Exception as e:
            raise ValueError("Failed to create database pool.") from e
        else:
            await self.create_tables()

    async def create_tables(self) -> None:
        async with utils.database.pool.acquire() as db:
            await db.execute(utils.database.SimpUser._table_create)

    @checks.is_owner()
    @commands.command()
    async def set_database_dsn(self, ctx: commands.Context, dsn: str) -> None:
        """Set the DSN for the database."""
        await self.config.database_dsn.set(dsn)
        try:
            utils.database.pool = await asyncpg.create_pool(dsn)
        except Exception as e:
            raise ValueError("Failed to create database pool.") from e
        else:
            await self.create_tables()
        await ctx.send("Database DSN set.")

    @checks.is_owner()
    @commands.command()
    async def drop_tables(self, ctx: commands.Context) -> None:
        """Drops all the tables in the database."""
        async with utils.database.pool.acquire() as db:
            await db.execute("DROP TABLE simp_users")
        await ctx.send("Tables dropped.")

    @checks.is_owner()
    @commands.command()
    async def create_tables(self, ctx: commands.Context) -> None:
        """Creates all the tables in the database."""
        await self.create_tables()
        await ctx.send("Tables created.")

    def cog_unload(self) -> None:
        async def close_pool():
            await utils.database.pool.close()

        self.bot.loop.create_task(close_pool())
