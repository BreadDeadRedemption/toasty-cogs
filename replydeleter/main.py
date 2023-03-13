from discord.ext import commands
from redbot.core import commands, checks, Config
import discord

class ReplyDeleter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = []

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if message is in one of the specified channels
        if message.channel.id in self.channels and message.reference is not None:
            # Delete the message
            await message.delete()

    @commands.group(name="replydelete", aliases=["rdel"])
    async def replydelete(self, ctx):
        """Group command for managing monitored channels"""
        pass

    @replydelete.command(name="addchannel")
    async def add_channel(self, ctx, channel: discord.TextChannel):
        """Add a channel to monitor for replies"""
        if channel.id not in self.channels:
            self.channels.append(channel.id)
            await ctx.send(f"Added channel {channel.mention} to monitored channels.")
        else:
            await ctx.send(f"Channel {channel.mention} is already being monitored.")

    @replydelete.command(name="removechannel")
    async def remove_channel(self, ctx, channel: discord.TextChannel):
        """Remove a channel from monitored channels"""
        if channel.id in self.channels:
            self.channels.remove(channel.id)
            await ctx.send(f"Removed channel {channel.mention} from monitored channels.")
        else:
            await ctx.send(f"Channel {channel.mention} is not being monitored.")
            
    @replydelete.command(name="list")
    async def list_channels(self, ctx):
        """List all the channels being monitored"""
        if not self.channels:
            await ctx.send("No channels are being monitored.")
        else:
            channel_mentions = [f"{self.bot.get_channel(channel_id).mention}" for channel_id in self.channels]
            await ctx.send(f"The following channels are being monitored: {', '.join(channel_mentions)}.")
