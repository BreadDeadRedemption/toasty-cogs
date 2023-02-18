import discord
from redbot.core import commands
from redbot.core import Config
import openai

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_global(chatgpt_api_key=None)
        self.api_key = None
        self.channel_id = None
        self.starting_prompt = None
        self.model_name = "davinci-3"
        openai.api_key = self.api_key

    async def _get_response(self, prompt, temperature):
        response = openai.Completion.create(
            engine=self.model_name,
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=temperature,
        )
        response_text = response.choices[0].text
        return response_text

    @commands.command()
    async def endchat(self, ctx):
        self.api_key = None
        self.channel_id = None
        self.starting_prompt = None
        await ctx.send("ChatGPT session ended")

    @commands.group()
    async def chatgpt(self, ctx):
        pass

    @chatgpt.command()
    async def setapikey(self, ctx, api_key):
        self.api_key = api_key
        await self.config.chatgpt_api_key.set(api_key)
        await ctx.send("OpenAI API key set")

    @chatgpt.command()
    async def setchannelid(self, ctx, channel):
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

    @chatgpt.command()
    async def setstartingprompt(self, ctx, starting_prompt):
        self.starting_prompt = starting_prompt
        await ctx.send("Starting prompt set")

    @chatgpt.command()
    async def chat(self, ctx, privacy="public"):
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

        await thread.send("Conversation started. Enter `chatgpt endchat` to end the conversation")
        while True:
            await thread.send(prompt)
            message = await self.bot.wait_for("message", check=lambda m: m.channel == thread and m.author == ctx.author)
            if message.content.lower() == "chatgpt endchat":
                break
            response_text = await self._get_response(prompt, temperature)
            prompt = f"{prompt.strip()} {response_text.strip()}"

        return
