import discord
from redbot.core import commands
import openai

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "your_openai_api_key_here"
        self.model_name = "your_openai_model_name_here"
        openai.api_key = self.api_key

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        response = openai.Completion.create(
            engine=self.model_name,
            prompt=message.content,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )

        response_text = response.choices[0].text
        await message.channel.send(response_text)