from discord.ext import commands
from redbot.core import commands, checks, Config

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
    async def add_channel(self, ctx, channel_id: int):
        """Add a channel to monitor for replies"""
        if channel_id not in self.channels:
            self.channels.append(channel_id)
            await ctx.send(f"Added channel {channel_id} to monitored channels.")
        else:
            await ctx.send(f"Channel {channel_id} is already being monitored.")

    @replydelete.command(name="removechannel")
    async def remove_channel(self, ctx, channel_id: int):
        """Remove a channel from monitored channels"""
        if channel_id in self.channels:
            self.channels.remove(channel_id)
            await ctx.send(f"Removed channel {channel_id} from monitored channels.")
        else:
            await ctx.send(f"Channel {channel_id} is not being monitored.")
            
    @replydelete.command(name="list")
    async def list_channels(self, ctx):
        """List all the channels being monitored"""
        if not self.channels:
            await ctx.send("No channels are being monitored.")
        else:
            channel_mentions = [f"<#{channel_id}>" for channel_id in self.channels]
            await ctx.send(f"The following channels are being monitored: {', '.join(channel_mentions)}.")
