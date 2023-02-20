import os
import discord
from discord.ext import commands
from src import responses
from src import log

logger = log.setup_logger(__name__)

isPrivate = False
isReplyAll = False

class ChatGPTCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="/chat | /help")

    @commands.command(name="chat", description="Have a chat with ChatGPT")
    async def chat(self, ctx, *, message: str):
        global isReplyAll
        if isReplyAll:
            await ctx.send("> **Warn: You already on replyAll mode. If you want to use slash command, switch to normal mode, use `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if ctx.author == self.bot.user:
            return
        username = str(ctx.author)
        user_message = message
        channel = str(ctx.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
        await self.send_message(ctx, user_message)

    async def send_message(self, ctx, user_message):
        global isReplyAll, isPrivate
        if not isReplyAll:
            await ctx.defer(ephemeral=isPrivate)
        try:
            response = '> **' + user_message + '** - <@' + str(ctx.author.id) + '> \n\n'
            response = f"{response}{await responses.handle_response(user_message)}"
            if len(response) > 1900:
                # Split the response into smaller chunks of no more than 1900 characters each (Discord limit is 2000 per chunk)
                if "```" in response:
                    # Split the response if the code block exists
                    parts = response.split("```")
                    # Send the first message
                    if isReplyAll:
                        await ctx.channel.send(parts[0])
                    else:
                        await ctx.send(parts[0])
                    # Send the code block in a separate message
                    code_block = parts[1].split("\n")
                    formatted_code_block = ""
                    for line in code_block:
                        while len(line) > 1900:
                            # Split the line at the 50th character
                            formatted_code_block += line[:1900] + "\n"
                            line = line[1900:]
                        formatted_code_block += line + "\n"  # Add the line and separate with a new line

                    # Send the code block in a separate message
                    if (len(formatted_code_block) > 2000):
                        code_block_chunks = [formatted_code_block[i:i+1900] for i in range(0, len(formatted_code_block), 1900)]
                        for chunk in code_block_chunks:
                            if isReplyAll:
                                await ctx.channel.send("```" + chunk + "```")
                            else:
                                await ctx.send("```" + chunk + "```")
                    else:
                         if isReplyAll:
                            await ctx.channel.send("```" + formatted_code_block + "```")
                        else:
                            await ctx.send("```" + formatted_code_block + "```")
                    # Send the remaining of the response in another message
                    if len(parts) >= 3:
                        if isReplyAll:
                            await ctx.channel.send(parts[2])
                        else:
                            await ctx.send(parts[2])
                else:
                    response_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for chunk in response_chunks:
                        if isReplyAll:
                            await ctx.channel.send(chunk)
                        else:
                            await ctx.send(chunk)
                        
            else:
                if isReplyAll:
                    await ctx.channel.send(response)
                else:
                    await ctx.send(response)
        except Exception as e:
            if isReplyAll:
                await ctx.channel.send("> **Error: Something went wrong, please try again later!**")
            else:
                await ctx.send("> **Error: Something went wrong, please try again later!**")
            logger.exception(f"Error while sending message: {e}")

    @commands.command(name="private", description="Toggle private access")
    async def private(self, ctx):
        global isPrivate
        await ctx.defer(ephemeral=False)
        if not isPrivate:
            isPrivate = not isPrivate
            logger.warning("\x1b[31mSwitch to private mode\x1b[0m")
            await ctx.send("> **Info: Next, the response will be sent via private message. If you want to switch back to public mode, use `/public`**")
        else:
            logger.info("You already on private mode!")
            await ctx.send("> **Warn: You already on private mode. If you want to switch to public mode, use `/public`**")

    @commands.command(name="public", description="Toggle public access")
    async def public(self, ctx):
        global isPrivate
        await ctx.defer(ephemeral=False)
        if isPrivate:
            isPrivate = not isPrivate
            await ctx.send("> **Info: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**")
            logger.warning("\x1b[31mSwitch to public mode\x1b[0m")
        else:
            await ctx.send("> **Warn: You already on public mode. If you want to switch to private mode, use `/private`**")
            logger.info("You already on public mode!")

    @commands.command(name="replyall", description="Toggle replyAll access")
    async def replyall(self, ctx):
        global isReplyAll
        await ctx.defer(ephemeral=False)
        if isReplyAll:
            await ctx.send("> **Info: The bot will only response to the slash command `/chat` next. If you want to switch back to replyAll mode, use `/replyAll` again.**")
            logger.warning("\x1b[31mSwitch to normal mode\x1b[0m")
        else:
            await ctx.send("> **Info: Next, the bot will response to all message in the server. If you want to switch back to normal mode, use `/replyAll` again.**")
            logger.warning("\x1b[31mSwitch to replyAll mode\x1b[0m")
        isReplyAll = not isReplyAll

    @commands.command(name="reset", description="Complete reset ChatGPT conversation history")
    async def reset(self, ctx):
        responses.chatbot.reset()
        await ctx.defer(ephemeral=False)
        await ctx.send("> Info: I have forgotten everything.")
        logger.warning("\x1b[31mChatGPT bot has been successfully reset\x1b[0m")
        await send_start_prompt(self)

    @commands.command(name="help", description="Show help for the bot")
    async def help(self, ctx):
        await ctx.defer(ephemeral=False)
        await ctx.send(""":star:**BASIC COMMANDS** \n
        - `/chat [message]` Chat with ChatGPT!
        - `/public` ChatGPT switch to public mode 
        - `/replyall` ChatGPT switch between replyall mode and default mode
        - `/reset` Clear ChatGPT conversation history\n
        For complete documentation, please visit https://github.com/Zero6992/chatGPT-discord-bot""")
        logger.info("\x1b[31mSomeone needs help!\x1b[0m")

async def on_message(self, message):
    if isReplyAll:
        if message.author == self.user:
            return
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
        await send_message(message, user_message)

async def on_command_error(self, ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("> **Error: The command is not found!**")
        logger.exception("Command not found!")
    else:
        logger.exception("An error occurred while processing a command.")
        await ctx.send("> **Error: Something went wrong, please try again later!**")
def setup(bot):
bot.add_cog(ChatGPT(bot))
