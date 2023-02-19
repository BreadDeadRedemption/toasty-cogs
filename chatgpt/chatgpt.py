import discord
from redbot.core import commands
from redbot.core import Config
import openai

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_guild(chatgpt_api_key=None)
        self.api_key = None
        self.channel_id = None
        self.starting_prompt = None
        self.model_name = "text-davinci-003"
        self.chat_active = False

    async def _get_api_key(self, guild):
        api_key = await self.config.guild(guild).chatgpt_api_key()
        return api_key

    async def _get_response(self, prompt, temperature, guild):
        api_key = await self._get_api_key(guild)
        openai.api_key = api_key
        prompt_len = len(self.starting_prompt)
        response = openai.Completion.create(
            engine=self.model_name,
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=temperature,
        )
        response_text = response.choices[0].text
        response_text = response_text[prompt_len:].strip()
        return response_text


    async def chat_check(self, ctx):
        if not self.chat_active:
            await ctx.send("No active chat session. Use the `chatgpt chat` command to start a new session")
            return False
        return True

    @commands.command()
    async def endchat(self, ctx):
        self.api_key = None
        self.channel_id = None
        self.starting_prompt = None
        self.chat_active = False
        await ctx.send("ChatGPT session ended")
        return
        
    @commands.group()
    async def chatgpt(self, ctx):
        pass

    @chatgpt.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setapikey(self, ctx, api_key):
        await self.config.guild(ctx.guild).chatgpt_api_key.set(api_key)
        await ctx.send("OpenAI API key set")

    @chatgpt.command()
    @commands.guild_only()
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
    @commands.guild_only()
    async def chat(self, ctx, privacy="public"):
        guild = ctx.guild
        api_key = await self._get_api_key(ctx.guild)
        if api_key is None:
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
            response_text = await self._get_response(prompt, temperature, guild)
            prompt = f"{prompt.strip()} {response_text.strip()}"

        return
