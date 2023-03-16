import discord
from discord.ext import commands
from redbot.core import commands
from redbot.core import Config, checks, bank
from redbot.core.commands import Context
from redbot.core.bot import Red
import random
import string
import asyncio

class AcroGame(commands.Cog, name="AcroGame"):
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        self.config.register_global(
            leaderboard={},
            reward=5000
        )
        self.config.register_guild(
            leaderboard={},
            reward=5000
        )
        self.config.register_member(
            wins=0,
            losses=0,
            highest_votes=0,
            highest_voted_acro=""
        )
        self.game_running = False

    async def red_delete_data_for_user(self, *, requester, user_id):
        await self.config.user_from_id(user_id).clear()

    @commands.group()
    async def acro(self, ctx: Context):
        pass

    def generate_acronym(self, length):
        acronym = ''
        for _ in range(length):
            letter = random.choice(string.ascii_uppercase)
            while letter in ['X', 'Z']:
                letter = random.choice(string.ascii_uppercase)
            acronym += letter + '.'
        return acronym[:-1]

    async def start_game(self, ctx: Context):
        if self.game_running:
            await ctx.send("A game of Acro is already running.")
            return None
        self.game_running = True
        acronym = self.generate_acronym(random.randint(3, 6))
        embed = discord.Embed(title="Acrophobia",
                              description=f"Game started. Create a sentence with the following acronym: {acronym}\nYou have 60 seconds to make a submission.",
                              color=0x42F56C)
        await ctx.send(embed=embed)
        return acronym

    async def gather_submissions(self, ctx: Context, acronym: str):
        if acronym is None:
            return []

        submissions = []
        submitted_users = set()

        def check(message):
            if message.author in submitted_users:
                return False
            words = message.content.upper().split()
            if len(words) == len(acronym.split('.')) and all([words[i][0] == acronym.split('.')[i] for i in range(len(acronym.split('.')))]):
                return True
            return False

        while True:
            try:
                submission = await self.bot.wait_for('message', timeout=60, check=check)
                submissions.append((submission.content, submission.author))
                submitted_users.add(submission.author)
                await submission.delete()
            except asyncio.TimeoutError:
                break

        return submissions
    async def voting_phase(self, ctx: Context, acronym: str, submissions: list):
        if not submissions:
            embed = discord.Embed(title="Acrophobia",
                                  description="No submissions received. Ending the game.",
                                  color=0x42F56C)
            await ctx.send(embed=embed)
            self.game_running = False
            return None

        embed = discord.Embed(title="Acrophobia - Submissions closed",
                              description=f"Acronym was {acronym}\n--",
                              color=0x42F56C)

        for i, (submission, _) in enumerate(submissions, start=1):
            embed.add_field(name=f"{i}. {submission}", value="\u200b", inline=False)

        embed.description += "--\nVote by typing a number of the submission"
        await ctx.send(embed=embed)

        votes = [0] * len(submissions)
        voters = set()

        def check(message):
            if message.author in voters or not message.content.isdigit():
                return False
            num = int(message.content) - 1
            if 0 <= num < len(submissions):
                return True
            return False

        while True:
            try:
                vote = await self.bot.wait_for('message', timeout=60, check=check)
                index = int(vote.content) - 1
                if submissions[index][1] != vote.author:
                    votes[index] += 1
                    voters.add(vote.author)
                    embed = discord.Embed(title="Acrophobia",
                                          description=f"{vote.author} cast their vote!",
                                          color=0x42F56C)
                    await ctx.send(embed=embed)
                await vote.delete()
            except asyncio.TimeoutError:
                break

        return votes

    async def end_game(self, ctx: Context, acronym: str, submissions: list, votes: list):
        if not votes:
            self.game_running = False
            return

        winner_index = votes.index(max(votes))
        winner = submissions[winner_index][1]
        reward = await self.config.guild(ctx.guild).reward()

        await bank.deposit_credits(winner, reward)

        await self.config.member(winner).wins.set(await self.config.member(winner).wins() + 1)
        for user in ctx.guild.members:
            if user != winner:
                await self.config.member(user).losses.set(await self.config.member(user).losses() + 1)

        if max(votes) > await self.config.member(winner).highest_votes():
            await self.config.member(winner).highest_votes.set(max(votes))
            await self.config.member(winner).highest_voted_acro.set(submissions[winner_index][0])

        embed = discord.Embed(title="Acrophobia",
                              description=f"Winner is {winner} with {max(votes)} votes.\nThey win {reward} {bank.get_currency_name(ctx.guild)}!\n{submissions[winner_index][0]}",
                              color=0x42F56C)
        await ctx.send(embed=embed)
        self.game_running = False

    @acro.command()
    async def start(self, ctx: Context):
        acronym = await self.start_game(ctx)
        submissions = await self.gather_submissions(ctx, acronym)
        votes = await self.voting_phase(ctx, acronym, submissions)
        await self.end_game(ctx, acronym, submissions, votes)

    @acro.command()
    async def leaderboard(self, ctx: Context):
        leaderboard = await self.config.guild(ctx.guild).leaderboard()
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:10]
        embed = discord.Embed(title="Acro Leaderboard", description="", color=0x42F56C)
        for i, (user_id, wins) in enumerate(sorted_leaderboard, start=1):
            user = self.bot.get_user(user_id)
            if user:
                embed.add_field(name=f"{i}. {user}", value=f"{wins} wins", inline=False)
        await ctx.send(embed=embed)

    @acro.command()
    async def stats(self, ctx: Context, user: discord.Member = None):
        if not user:
            user = ctx.author
        stats = await self.config.member(user).all()
        embed = discord.Embed(title=f"{user}'s Acro Stats", description="", color=0x42F56C)
        embed.add_field(name="Wins", value=stats["wins"])
        embed.add_field(name="Losses", value=stats["losses"])
        embed.add_field(name="W/L Ratio", value=f"{stats['wins'] / (stats['wins'] + stats['losses']):.2f}")
        embed.add_field(name="Highest Voted Acro", value=stats["highest_voted_acro"])
        embed.add_field(name="Highest Votes", value=stats["highest_votes"])
        await ctx.send(embed=embed)

    @acro.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def set_reward(self, ctx: Context, reward: int):
        if reward <= 0:
            await ctx.send("Reward must be a positive number.")
            return
        await self.config.guild(ctx.guild).reward.set(reward)
        await ctx.send(f"Reward for winning Acro is now set to {reward} {bank.get_currency_name(ctx.guild)}.")

def setup(bot: Red):
    bot.add_cog(AcroGame(bot))
