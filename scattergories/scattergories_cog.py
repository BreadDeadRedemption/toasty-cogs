from redbot.core import commands
import random
import asyncio
from typing import Dict, List, Tuple
from discord import User

class ScattergoriesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.categories = [
            "Fruits",
            "Animals",
            "Countries",
            "Things found in the kitchen",
            "Colors",
            "Types of shoes",
            "Sports",
            "Musical instruments",
            "School subjects",
            "Flowers",
            "Things that are round",
            "Types of cheese",
            "Items you can wear",
            "Words ending in 'ing'",
            "Famous people",
            "Things that are cold",
            "Things you find in a park",
            "Vegetables",
            "Things that are sticky",
            "Items you find in a grocery store",
            "Things you can drink",
            "Insects",
            "TV shows",
            "Items you find in a toolbox"
        ]
        self.players = []
        self.answers = {}
        self.current_category = None
        self.current_letter = None
        self.round_timer = None
        self.voting_time = 60

    @commands.command()
    async def join(self, ctx):
        player = ctx.message.author
        if player not in self.players:
            self.players.append(player)
            await ctx.send(f"{player.mention} has joined the game.")

    @commands.command()
    async def unjoin(self, ctx):
        player = ctx.message.author
        if player in self.players:
            self.players.remove(player)
            await ctx.send(f"{player.mention} has left the game.")

    @commands.command()
    async def start(self, ctx):
        if len(self.players) < 2:
            await ctx.send("Not enough players to start the game.")
            return
        self.current_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.current_category = self.categories[0]
        self.answers = {player: [] for player in self.players}
        for category in self.categories:
            self.current_category = category
            self.round_timer = asyncio.create_task(self.countdown_timer(ctx, 180))
            await ctx.send(f"Hey there, welcome to Scattergories! You have 180 seconds to give an item that fits into each of the following categories starting with the letter {self.current_letter}. Your categories are:\n{self.current_category}")
            await asyncio.sleep(180)
            self.round_timer.cancel()
            await self.collect_answers(ctx)
            await self.show_answers(ctx)
            await self.start_voting(ctx)

    async def countdown_timer(self, ctx, seconds: int):
        while seconds > 0:
            await ctx.send(f"Time remaining: {seconds} seconds")
            await asyncio.sleep(1)
            seconds -= 1
        await ctx.send("Time's up!")

    async def collect_answers(self, ctx):
        for player in self.players:
            await player.send(f"Category: {self.current_category}\nStarts with: {self.current_letter}\nYou have 180 seconds to give your answers separated by commas:")
            def check(msg):
                return msg.author == player and msg.channel.type == discord.ChannelType.private
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=180)
                answers = msg.content.strip().split(",")
                self.answers[player] = [answer.strip() for answer in answers]
            except asyncio.TimeoutError:
                await player.send("Time's up!")

    async def show_answers(self, ctx):
        for player, answers in self.answers.items():
            await ctx.send(f"{player.name}'s answers for {self.current_category}: {', '.join(answers)}")

    async def start_voting(self, ctx):
        await ctx.send("Time's up! Voting begins now!")
        await asyncio.sleep(5)
        for player in self.players:
            await player.send("It's time to vote! You have 60 seconds to vote for your favorite answer in each category.")
        for i in range(len(self.categories)):
            category = self.categories[i]
            answers = {player: self.answers[player][i] for player in self.players if len(self.answers[player]) > i}
            await ctx.send(f"Category {i+1}: {category}")
            scores = {answer: 0 for answer in answers.values()}
            for player, answer in answers.items():
                await ctx.send(f"{player.name}: {answer}")
                for emoji in ["\U0001F44D", "\U0001F44E"]:
                    await ctx.message.add_reaction(emoji)
                    def check(reaction, user):
                        return user != reaction.message.author and user == player and str(reaction) in ["\U0001F44D", "\U0001F44E"]
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=self.voting_time)
                        if str(reaction) == "\U0001F44D":
                            scores[answer] += 1
                        else:
                            scores[answer] -= 1
                    except asyncio.TimeoutError:
                        pass
            await ctx.send("Voting is over!")
            await asyncio.sleep(5)
            await self.show_scores(ctx, scores)

    async def show_scores(self, ctx, scores: Dict[str, int]):
        sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
        top_score = sorted_scores[0][1]
        winners = [answer for answer, score in sorted_scores if score >= top_score]
        if len(winners) == 1:
            await ctx.send(f"The winner for {self.current_category} is: {winners[0]}")
        else:
            await ctx.send(f"There was a tie for {self.current_category} between: {', '.join(winners)}")
            self.categories.insert(0, self.current_category)
        self.current_category = None
        self.current_letter = None
        self.answers = {}
               
