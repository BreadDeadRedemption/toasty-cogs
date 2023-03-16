import discord
from discord.ext import commands
from redbot.core import Config, checks
from redbot.core.commands import Context
from redbot.core.bot import Red
from redbot.core import commands
from redbot.core import bank
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

    async def red_delete_data_for_user(self, *, requester, user_id):
        await self.config.user_from_id(user_id).clear()

    @commands.group()
    async def acro(self, ctx: Context):
        pass
    def generate_acronym(self):
        acronym = ''
        for _ in range(3):
            letter = random.choice(string.ascii_uppercase)
            while letter in ['X', 'Z']:
                letter = random.choice(string.ascii_uppercase)
            acronym += letter
        return acronym

    async def start_game(self, ctx: Context):
        acronym = self.generate_acronym()
        embed = discord.Embed(title="Acrophobia",
                              description=f"Game started. Create a sentence with the following acronym: {acronym}\nYou have 60 seconds to make a submission.",
                              color=0x42F56C)
        await ctx.send(embed=embed)
        return acronym

    async def gather_submissions(self, ctx: Context, acronym: str):
        submissions = []
        def check(message):
            words = message.content.upper().split()
            if len(words) == len(acronym) and all([words[i][0] == acronym[i] for i in range(len(acronym))]):
                return True
            return False

        while True:
            try:
                submission = await self.bot.wait_for('message', timeout=60, check=check)
                submissions.append((submission.content, submission.author))
                await submission.delete()
            except asyncio.TimeoutError:
                break

        return submissions
    async def voting_phase(self, ctx: Context, submissions):
        if not submissions:
            embed = discord.Embed(title="Acrophobia",
                                  description="No submissions received. The game has ended.",
                                  color=0xFF0000)
            await ctx.send(embed=embed)
            return

        description = "Acrophobia - Submissions closed\n"
        acronym = submissions[0][0].split()[0][0] + submissions[0][0].split()[1][0] + submissions[0][0].split()[2][0]
        description += f"Acronym was {acronym}\n--\n"
        for idx, submission in enumerate(submissions, 1):
            description += f"{idx}. {submission[0]}\n"

        embed = discord.Embed(title="Acrophobia",
                              description=description + "--\nVote by typing the number of the submission.",
                              color=0x42F56C)
        await ctx.send(embed=embed)

        votes = [0] * len(submissions)

        def check(message):
            if message.content.isdigit():
                num = int(message.content)
                if 1 <= num <= len(submissions) and message.author != submissions[num - 1][1]:
                    return True
            return False

        while True:
            try:
                vote = await self.bot.wait_for('message', timeout=30, check=check)
                votes[int(vote.content) - 1] += 1
                embed = discord.Embed(title="Acrophobia",
                                      description=f"{vote.author} cast their vote!",
                                      color=0x42F56C)
                await ctx.send(embed=embed)
                await vote.delete()
            except asyncio.TimeoutError:
                break

        winner_idx = votes.index(max(votes))
        winner = submissions[winner_idx][1]
        winning_acro = submissions[winner_idx][0]
        await self.config.member(winner).wins.set(await self.config.member(winner).wins() + 1)

        reward = await self.config.guild(ctx.guild).reward()
        currency_name = await bank.get_currency_name(ctx.guild)
        await bank.deposit_credits(winner, reward)

        embed = discord.Embed(title="Acrophobia",
                              description=f"Winner is {winner} with {max(votes)} votes.\nThey win {reward} {currency_name}!\n{winning_acro}",
                              color=0x42F56C)
        await ctx.send(embed=embed)

    @acro.command()
    async def play(self, ctx: Context):
        acronym = await self.start_game(ctx)
        submissions = await self.gather_submissions(ctx, acronym)
        await self.voting_phase(ctx, submissions)
    @acro.command()
    async def leaderboard(self, ctx: Context):
        leaderboard = await self.config.guild(ctx.guild).leaderboard()
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)

        def create_embed(page):
            embed = discord.Embed(title="Acrophobia Leaderboard",
                                  description=f"Top 10 players in {ctx.guild.name}",
                                  color=0x42F56C)
            start = (page - 1) * 10
            end = start + 10
            for rank, (user_id, wins) in enumerate(sorted_leaderboard[start:end], start=start + 1):
                user = self.bot.get_user(user_id)
                embed.add_field(name=f"{rank}. {user}", value=f"Wins: {wins}", inline=False)
            return embed

        embed = create_embed(1)
        leaderboard_message = await ctx.send(embed=embed)

        if len(sorted_leaderboard) > 10:
            left_arrow = "⬅️"
            right_arrow = "➡️"
            await leaderboard_message.add_reaction(left_arrow)
            await leaderboard_message.add_reaction(right_arrow)

            def check(reaction, user):
                return user == ctx.author and reaction.emoji in [left_arrow, right_arrow]

            page = 1
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
                    await reaction.remove(user)
                    if reaction.emoji == left_arrow and page > 1:
                        page -= 1
                    elif reaction.emoji == right_arrow and page * 10 < len(sorted_leaderboard):
                        page += 1
                    embed = create_embed(page)
                    await leaderboard_message.edit(embed=embed)
                except asyncio.TimeoutError:
                    break

    @acro.command()
    async def stats(self, ctx: Context, user: discord.Member = None):
        if not user:
            user = ctx.author

        wins = await self.config.member(user).wins()
        losses = await self.config.member(user).losses()
        wl_ratio = wins / (wins + losses) if wins + losses > 0 else 0
        highest_votes = await self.config.member(user).highest_votes()
        highest_voted_acro = await self.config.member(user).highest_voted_acro()

        embed = discord.Embed(title=f"Acrophobia Stats for {user}",
                              color=0x42F56C)
        embed.add_field(name="Wins", value=wins)
        embed.add_field(name="Losses", value=losses)
        embed.add_field(name="W/L Ratio", value=f"{wl_ratio:.2f}")
        embed.add_field(name="Highest Voted Submission", value=f"{highest_voted_acro} ({highest_votes} votes)")

        await ctx.send(embed=embed)

    @acro.command()
    @checks.admin()
    async def set_reward(self, ctx: Context, value: int):
        await self.config.guild(ctx.guild).reward.set(value)
        embed = discord.Embed(title="Acrophobia",
                              description=f"Reward for winning the game has been set to {value}.",
                              color=0x42F56C)
        await ctx.send(embed=embed)

def setup(bot: Red):
    bot.add_cog(AcroGame(bot))
