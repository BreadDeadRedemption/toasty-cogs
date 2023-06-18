from redbot.core import commands
from random import choice, randint
from string import ascii_uppercase
from collections import defaultdict
from asyncio import Semaphore, sleep

class Acrophobia(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.submission_time = 60
        self.vote_time = 30
        self.current_phase = "Submission"
        self.starting_letters = []
        self.submissions = defaultdict(int)
        self.users_who_voted = set()
        self.lock = Semaphore(1)

    def initialize_starting_letters(self):
        word_count = randint(3, 6)
        self.starting_letters = [choice([c for c in ascii_uppercase if c not in 'XZ']) for _ in range(word_count)]

    async def user_input(self, user_id, user_name, input):
        user = (user_id, user_name, input.title())
        await self.lock.acquire()
        try:
            if self.current_phase == "Submission":
                if user in self.submissions or not self.is_valid_answer(input):
                    return False
                self.submissions[user] = 0
                return True
            elif self.current_phase == "Voting":
                if not input.isdigit() or not (0 <= (index := int(input) - 1) < len(self.submissions)):
                    return False
                to_vote_for = list(self.submissions.keys())[index]
                if to_vote_for[0] == user_id or user_id in self.users_who_voted:
                    return False
                self.submissions[to_vote_for] += 1
                self.users_who_voted.add(user_id)
                return True
            return False
        finally:
            self.lock.release()

    def is_valid_answer(self, input):
        input = input.upper()
        input_words = input.split(' ')
        if len(input_words) != len(self.starting_letters):
            return False
        for i, letter in enumerate(self.starting_letters):
            if not input_words[i].startswith(letter):
                return False
        return True

    @commands.command()
    async def run(self, ctx):
        self.initialize_starting_letters()
        await ctx.send(f"Game started with letters: {self.starting_letters}")
        await sleep(self.submission_time)
        await self.lock.acquire()
        try:
            if len(self.submissions) == 0:
                self.current_phase = "Ended"
                await ctx.send("No submissions, game ended.")
                return
            if len(self.submissions) == 1:
                self.current_phase = "Ended"
                await ctx.send(f"Only one submission, winner is {list(self.submissions.keys())[0][1]}")
                return
            self.current_phase = "Voting"
            await ctx.send("Voting phase started.")
        finally:
            self.lock.release()
        await sleep(self.vote_time)
        await self.lock.acquire()
        try:
            self.current_phase = "Ended"
            winner = max(self.submissions, key=self.submissions.get)
            await ctx.send(f"Game ended, winner is {winner[1]} with acronym {winner[2]}")
        finally:
            self.lock.release()

def setup(bot):
    bot.add_cog(Acrophobia(bot))
