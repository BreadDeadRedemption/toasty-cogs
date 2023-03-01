import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import box

class Acro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.acro_dict = {}
        self.acro_ongoing = False
        self.acro_submission = {}
        self.acro_votes = {}
        self.acro_reward = 5000 # Default reward
        self.acro_leaderboard = {}

    @commands.command()
    async def acro(self, ctx):
        if self.acro_ongoing:
            await ctx.send("A game of Acro is already ongoing.")
            return
        self.acro_ongoing = True
        acronym = await self.get_random_acronym()
        embed = discord.Embed(title="Acrophobia", description=f"Game started. Create a sentence with the following acronym: {acronym}\nYou have 60 seconds to make a submission.", color=discord.Color.blue())
        await ctx.send(embed=embed)
        self.acro_dict[ctx.guild.id] = acronym
        self.acro_submission[ctx.guild.id] = {}
        self.acro_votes[ctx.guild.id] = {}
        self.acro_leaderboard[ctx.guild.id] = {}
        await self.collect_submissions(ctx)
        await self.vote_submissions(ctx)

    async def get_random_acronym(self):
        import random
        import string
        letters = string.ascii_uppercase.replace("X", "").replace("Z", "")
        return "".join(random.choice(letters) for i in range(3))

    async def collect_submissions(self, ctx):
        def check(message):
            return message.guild == ctx.guild and message.content.upper() == self.acro_dict[ctx.guild.id].upper() and not message.author.bot

        try:
            while True:
                message = await self.bot.wait_for('message', timeout=60, check=check)
                self.acro_submission[ctx.guild.id][message.author.id] = message.content
                await message.delete()
        except:
            pass

    async def vote_submissions(self, ctx):
        submissions = list(self.acro_submission[ctx.guild.id].values())
        if not submissions:
            await ctx.send("No submissions were received. The game is cancelled.")
            self.acro_ongoing = False
            return
        submission_list = ["--"]
        for i, submission in enumerate(submissions):
            submission_list.append(f"{i+1}. {submission}")
            self.acro_votes[ctx.guild.id][i+1] = []
        submission_list.append("--")
        embed = discord.Embed(title="Acrophobia - Submissions closed", description=f"Acronym was {self.acro_dict[ctx.guild.id]}\n\n" + "\n".join(submission_list), color=discord.Color.blue())
        message = await ctx.send(embed=embed)
        for i in range(1, len(submissions)+1):
            await message.add_reaction(str(i))
        try:
            while True:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=lambda reaction, user: user != self.bot.user and reaction.message.id == message.id and str(reaction.emoji) in [str(i) for i in range(1, len(submissions)+1)])
                vote = int(str(reaction.emoji))
                if vote not in self.acro_votes[ctx.guild.id][vote]:
                    self.acro_votes[ctx.guild.id][vote].append(user.id)
                if user.id not in self.acro_votes[ctx.guild.id][vote]:
                    self.acro_votes[ctx.guild.id][vote].append(user.id)
            await reaction.message.remove_reaction(reaction, user)
        except:
            pass
        votes = {}
        for i, submission in enumerate(submissions):
            votes[i+1] = len(self.acro_votes[ctx.guild.id][i+1])
        max_vote = max(votes.values())
        winners = [i for i, vote in votes.items() if vote == max_vote]
        if len(winners) == 1:
            winner = winners[0]
            winning_submission = submissions[winner-1]
            winner_name = await self.bot.fetch_user(list(self.acro_votes[ctx.guild.id][winner])[0])
            self.acro_leaderboard[ctx.guild.id][winner_name.id] = self.acro_leaderboard[ctx.guild.id].get(winner_name.id, 0) + 1
            await ctx.send(f"Acrophobia\nWinner is {winner_name.name} with {max_vote} votes.\nThey win {self.acro_reward} credits!\n{winning_submission}")
        else:
            await ctx.send("Acrophobia\nThere was a tie. No one wins.")

@commands.command()
async def acro_leaderboard(self, ctx):
    guild_id = ctx.guild.id
    leaderboard = self.acro_leaderboard[guild_id]
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    page = 1
    pages = len(sorted_leaderboard) // 10 + 1
    while True:
        start = (page-1)*10
        end = start + 10
        leaderboard_str = ""
        for i, item in enumerate(sorted_leaderboard[start:end]):
            user = await self.bot.fetch_user(item[0])
            leaderboard_str += f"{i+start+1}. {user.name} - {item[1]}\n"
        embed = discord.Embed(title=f"Acro Leaderboard (Server)", description=leaderboard_str, color=discord.Color.blue())
        embed.set_footer(text=f"Page {page}/{pages}")
        await ctx.send(embed=embed)
        if pages > 1:
            await ctx.send("React with ◀ to go to the previous page or ▶ to go to the next page.")
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=lambda reaction, user: user != self.bot.user and reaction.message.id == message.id and str(reaction.emoji) in ["◀", "▶"])
                if str(reaction.emoji) == "◀" and page > 1:
                    page -= 1
                elif str(reaction.emoji) == "▶" and page < pages:
                    page += 1
                await reaction.message.remove_reaction(reaction, user)
            except:
                break
        else:
            break

@commands.command()
async def acro_stats(self, ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    guild_id = ctx.guild.id
    total_wins = self.acro_leaderboard[guild_id].get(user.id, 0)
    total_played = sum(1 for submission in self.acro_submission[guild_id].values() if submission != {})
    win_loss_ratio = total_wins / total_played if total_played > 0 else 0
    submissions = [submission for submission in self.acro_submission[guild_id].values() if submission != {}]
    max_votes = 0
    for i, submission in enumerate(submissions):
        if len(self.acro_votes[guild_id][i+1]) > max_votes:
            max_votes = len(self.acro_votes[guild_id][i+1])
            winning_submission = submission
        embed = discord.Embed(title=f"{user.name}'s Acro Stats", color=discord.Color.blue())
        embed.add_field(name="Total Wins", value=total_wins)
        embed.add_field(name="Total Played", value=total_played)
        embed.add_field(name="Win/Loss Ratio", value=win_loss_ratio)
        if max_votes > 0:
            embed.add_field(name="Most Popular Submission", value=winning_submission)
        await ctx.send(embed=embed)

    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def acro_set(self, ctx):
        pass

    @acro_set.command()
    async def reward(self, ctx, value: int):
        self.acro_reward = value
        await ctx.send(f"Acro reward set to {value} credits.")
            
