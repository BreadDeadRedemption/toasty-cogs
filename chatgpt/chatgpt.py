import discord
from redbot.core import commands, Config
import openai

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = None
        self.model_name = "davinci-3"
        self.channel_id = None
        self.starting_prompt = None
        self.config = Config.get_conf(self, identifier=1234567890)

    async def _get_response(self, message_content, temperature):
        if self.api_key is None:
            raise ValueError("API key must be set")

        openai.api_key = self.api_key
        response = openai.Completion.create(
            engine=self.model_name,
            prompt=message_content,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=temperature,
        )
        response_text = response.choices[0].text
        return response_text

    @commands.command()
    async def chatgpt_setapikey(self, ctx, api_key):
        self.api_key = api_key
        await self.config.chatgpt_api_key.set(api_key)
        await ctx.send("OpenAI API key set")

    @commands.command()
    async def chatgpt_setchannelid(self, ctx, channel):
        if channel.startswith("<#") and channel.endswith(">"):
            channel = channel[2:-1]

        channel_id = None
        for ch in ctx.guild.channels:
            if ch.id == int(channel) or ch.name == channel:
                channel_id = ch.id
                break

        if channel_id is None:
            await ctx.send("Invalid channel ID or mention")
            return

        self.channel_id = channel_id
        await ctx.send(f"Channel ID set to {channel_id}")

    @commands.command()
    async def chatgpt_setstartingprompt(self, ctx, starting_prompt):
        self.starting_prompt = starting_prompt
        await ctx.send("Starting prompt set")

    @commands.command()
    async def chatgpt_chat(self, ctx, privacy="public"):
        self.api_key = await self.config.chatgpt_api_key()

        if self.api_key is None:
            await ctx.send("API key must be set before chatting")
            return

        if self.channel_id is not None and ctx.channel.id != self.channel_id:
            await ctx.send("This command can only be used in the designated chat channel")
            return

        if privacy == "private":
            thread = await ctx.author.create_dm()
        else:
            thread = ctx.channel

        await thread.send("Starting conversation with ChatGPT. Please enter your initial prompt:")
        message = await self.bot.wait_for("message", check=lambda m: m.channel == thread and m.author == ctx.author)
        prompt = message.content

        await thread.send("Please enter the temperature (a floating-point number between 0 and 1) for the model:")
        message = await self.bot.wait_for("message", check=lambda m: m.channel == thread and m.author == ctx.author)
        try:
            temperature = float(message.content)
        except ValueError:
            await thread.send("Invalid temperature value. Please enter a floating-point number between 0 and 1")
            return

        await thread.send("Conversation started. Enter `chatgpt endchat` to end the conversation.")
        while True:
            message = await self.bot.wait_for("message", check=lambda m: m.channel == thread and m.author == ctx.author)
            if message.content == "chatgpt endchat":
                await thread.send("Conversation ended")
                return
            response_text = await self._get_response
