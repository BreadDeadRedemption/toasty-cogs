from redbot.core import commands
import discord

class ThreadFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_threads = []
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.Thread):
            if message.channel.id not in self.active_threads: # Check if the thread is active
                return
            if not message.author.permissions_in(message.channel).administrator:
                await message.delete()
                
    @commands.command()
    async def threadfilter(self, ctx, thread_id: int):
        thread = discord.utils.get(self.bot.get_all_channels(), id=thread_id)
        if not isinstance(thread, discord.abc.Messageable):
            return await ctx.send("Invalid thread ID.")
        if thread.id in self.active_threads:
            return await ctx.send("Thread is already active.")
        await thread.add_user(self.bot.user) # Add the bot to the thread
        self.active_threads.append(thread.id)
        await ctx.send(f"Thread {thread.name} is now being filtered.")

        
    @commands.command()
    async def removethread(self, ctx, thread_id: int):
        thread = await self.bot.fetch_channel(thread_id)
        if not isinstance(thread, discord.Thread):
            return await ctx.send("Invalid thread ID.")
        if thread.id not in self.active_threads:
            return await ctx.send("Thread is not active.")
        await thread.remove_user(self.bot.user) # Remove the bot from the thread
        self.active_threads.remove(thread.id)
        await ctx.send(f"Thread {thread.name} is no longer being filtered.")
        
def setup(bot):
    cog = ThreadFilterCog(bot)
    bot.add_cog(cog)
