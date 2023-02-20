from redbot.core import commands
import discord
from discord.ext import commands
from typing import Dict
from collections import Counter

class AcroCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.submissions = {}
        self.author_submissions = {}
        self.votes = {}
        self.current_phase = "inactive"
        self.players = []
        self.tiebreak_winners = []
        self.tiebreak_votes = {}

    async def acro_loop(self):
        self.current_phase = "submission"
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            if self.current_phase == "submission":
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.players)} players"))
                await self.start_submissions()
                await self.bot.change_presence(activity=None)
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Voting for {len(self.submissions)} submissions"))
                self.current_phase = "voting"
            elif self.current_phase == "voting":
                await self.start_voting()
                self.current_phase = "inactive"
                await self.update_leaderboard(self.get_leaderboard(self.winners()))
                await self.end_game()
            else:
                await self.bot.change_presence(activity=None)
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{self.bot.command_prefix}acro start"))
                await self.acro_on_cooldown(300)
                await self.bot.change_presence(activity=None)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.current_phase == "submission" and message.channel.id == self.submissions_channel.id:
            if message.author not in self.players:
                return
            self.submissions[message.author.id] = message.content.lower()
            self.author_submissions[message.author.id] = str(message.author)
            await message.delete()
        elif self.current_phase == "voting" and message.channel.id == self.votes_channel.id:
            if message.author.id in self.votes or not message.content.isnumeric():
                return
            vote = int(message.content)
            if vote > 0 and vote <= len(self.submissions):
                self.votes[message.author.id] = vote
                await message.add_reaction("✅")

        await self.check_votes()

    @commands.group(name="acro", invoke_without_command=True)
    async def acro(self, ctx):
        """Starts a game of acrophobia"""
        await ctx.send_help(ctx.command)

    @acro.command(name="start")
    @commands.cooldown(rate=1, per=300, type=commands.BucketType.guild)
    async def acro_start(self, ctx):
        """Starts a game of acrophobia"""
        if self.current_phase != "inactive":
            await ctx.send("There's already a game in progress.")
            return

        self.players = [member for member in ctx.guild.members if not member.bot and not member.voice.self_mute and not member.voice.deaf]
        if len(self.players) < 3:
            await ctx.send("There must be at least 3 players to start a game.")
            return

        self.submissions_channel = await ctx.guild.create_text_channel("acro-submissions", category=ctx.channel.category, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)})
        self.votes_channel = await ctx.guild.create_text_channel("acro-votes", category=ctx.channel.category, overwrites={ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)})
                                                                                                                          
    async def start_game(self, ctx):
        self.playing = True
        self.submissions.clear()
        self.votes.clear()
        self.current_round += 1
        self.current_acro = generate_acro()
        self.submissions_channel = ctx.channel
        await ctx.send(f"Acrophobia game started in {self.submissions_channel.mention}. Players, submit your acronyms for the round starting with the letters {self.current_acro}.")
        await asyncio.sleep(1)
        await self.set_game_channel(ctx.channel.id)

        
        for player in self.players:
            try:
                await player.send(f"Acrophobia game started in {self.submissions_channel.mention}. Submit your answer in this channel.")
            except discord.errors.Forbidden:
                continue

        await self.acro_loop.start()

    async def acro_on_cooldown(self, duration: int):
        await asyncio.sleep(duration)
        await self.submissions_channel.send(f"Acrophobia game is now on cooldown for {duration} seconds.")

    async def start_submissions(self):
        self.submissions = {}
        self.author_submissions = {}
        self.votes = {}
        self.tiebreak_winners = []
        self.tiebreak_votes = {}
        await self.submissions_channel.purge(limit=1000)

        submission_prompt = "Enter your acrophobia submission:"
        for player in self.players:
            try:
                await player.send(submission_prompt)
            except discord.errors.Forbidden:
                continue

        await asyncio.sleep(60)
        await self.submissions_channel.send("Time's up! Voting starts now.")

    async def start_voting(self):
        self.votes = {}
        await self.votes_channel.purge(limit=1000)

        submissions_output = "```"
        for i, (author_id, submission) in enumerate(self.submissions.items()):
            author = self.author_submissions[author_id]
            submissions_output += f"{i + 1}. {submission} (Submitted by: {author})\n"
        submissions_output += "```"

        await self.votes_channel.send(submissions_output)

    async def end_game(self):
        winners = self.winners()
        if len(winners) == 0:
            await self.submissions_channel.send("No one submitted a valid entry. Game over.")
            await self.submissions_channel.delete()
            await self.votes_channel.delete()
            await self.acro_loop.stop()
            return
        elif len(winners) == 1:
            winner_id = winners[0]["id"]
            winner_name = winners[0]["name"]
            await self.submissions_channel.send(f"{winner_name} won with their submission: {self.submissions[winner_id]}")
        else:
            self.tiebreak_winners = winners
            self.tiebreak_votes = {}
            self.current_phase = "tiebreak"
            await self.start_tiebreak()

        await self.submissions_channel.delete()
        await self.votes_channel.delete()
        await self.acro_loop.stop()

    def winners(self) -> Dict:
        if len(self.submissions) == 0:
            return []

        submission_count = Counter(self.submissions.values())
        top_submission_count = submission_count.most_common(1)[0][1]
        top_submissions = [submission for submission, count in submission_count.items() if count == top_submission_count]

        return [{"id": author_id, "name": self.author_submissions[author_id], "submission": submission, "wins": submission_count[submission], "losses": len(self.submissions) - submission_count[submission]} for author_id, submission in self.submissions.items() if submission in top_submissions]

    async def start_tiebreak(self):
        self.votes = {}
        await self.votes_channel.purge(limit=1000)

        submissions_output = "```"
        for i, (author_id, submission) in enumerate(self.submissions.items()):
            author = self.author_submissions[author_id]
            if submission in [winner["submission"] for winner in self.tiebreak_winners]:
                          self.tiebreak_votes[submission] = {"votes": 0, "authors": []}
            submissions_output += f"{i + 1}. {submission} (Submitted by: {author})\n"
        submissions_output += "```"

        tiebreak_instructions = "The game has resulted in a tie. Please vote for your favorite submission using the numbers.\n"
        for submission, data in self.tiebreak_votes.items():
            tiebreak_instructions += f"{submission}: {data['votes']}\n"
        await self.votes_channel.send(tiebreak_instructions)
        await self.votes_channel.send(submissions_output)

    async def handle_vote(self, message: discord.Message):
        if self.current_phase == "voting":
            try:
                vote = int(message.content)
                author_id = message.author.id
                submission = self.submissions[author_id]
                if vote in self.votes.values():
                    return await message.channel.send("You've already voted for that submission.")
                if vote < 1 or vote > len(self.submissions):
                    return await message.channel.send(f"Please vote between 1 and {len(self.submissions)}.")
                self.votes[author_id] = vote
                if len(self.votes) == len(self.submissions):
                    await self.start_tiebreak()
                else:
                    await message.channel.send(f"Vote for {submission} counted.")
            except ValueError:
                pass

        elif self.current_phase == "tiebreak":
            try:
                vote = int(message.content)
                submission = list(self.tiebreak_votes.keys())[vote - 1]
                author_id = list(self.submissions.keys())[list(self.submissions.values()).index(submission)]
                if author_id in self.tiebreak_votes[submission]["authors"]:
                    return await message.channel.send("You've already voted for that submission.")
                self.tiebreak_votes[submission]["votes"] += 1
                self.tiebreak_votes[submission]["authors"].append(author_id)
                await message.channel.send(f"Vote for {submission} counted.")
                await self.check_tiebreak_votes()
            except (ValueError, IndexError):
                pass

    async def check_tiebreak_votes(self):
        for submission, data in self.tiebreak_votes.items():
            if data["votes"] == len(self.tiebreak_winners):
                await self.submissions_channel.send(f"{submission} won with {data['votes']} votes in the tiebreak round.")
                await self.end_game()
                return

    async def start(self, ctx):
        self.submissions_channel = ctx.channel
        self.players = [member for member in self.submissions_channel.members if not member.bot]

        if len(self.players) < 2:
            await ctx.send("Acrophobia requires at least two players to start.")
            return

        self.current_phase = "submissions"
        await self.submissions_channel.send("Acrophobia starting in 10 seconds.")
        await asyncio.sleep(10)

        self.acro_loop.start()


class Acro(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def acro(self, ctx):
        await ctx.send_help(ctx.command)

    @acro.command()
    async def start(self, ctx):
        acro_game = Acrophobia()
        await acro_game.start(ctx)

    @acro.command()
    async def leaderboard(self, ctx):
        guild_id = str(ctx.guild.id)
        winners = await bank.get_leaderboard(10, guild_id, _key=lambda x: x.startswith("acro_wins_"))
        if not winners:
            return await ctx.send("There are no winners yet.")
    
        output = "Acro leaderboard:\n```"
        for winner in winners:
            user = ctx.guild.get_member(winner["id"])
            output.append(f"{user.display_name}: {winner['wins']} wins, {winner['losses']} losses")
        output = "\n".join(output)
        await ctx.send(box(output, lang="ini"))

    @acro.command()
    async def me(self, ctx):
        user_id = str(ctx.author.id)
        wins = await bank.get_balance(user_id, "acro_wins")
        losses = await bank.get_balance(user_id, "acro_losses")
        await ctx.send(f"{ctx.author.display_name}, your Acrophobia stats: {wins} wins, {losses} losses.")
