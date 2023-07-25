from redbot.core import commands  # isort:skip
from redbot.core.i18n import Translator  # isort:skip
import discord  # isort:skip
import typing  # isort:skip
import asyncio
import datetime
import random
import string
from collections import Counter
from prettytable import PrettyTable
from redbot.core.utils.chat_formatting import box, humanize_list
_ = Translator("AcronymGame", __file__)
class JoinGameModal(discord.ui.Modal):
    def __init__(self, parent: discord.ui.View) -> None:
        super().__init__(title="Join Acronym Game")
        self._parent: discord.ui.View = parent
        self.answer: discord.ui.TextInput = discord.ui.TextInput(
            label=f"Answer for {self._parent.acronym} acronym",
            placeholder=f"Your full name for {self._parent.acronym} acronym",
            default=None,
            style=discord.TextStyle.short,
            custom_id="description",
            required=True,
            min_length=(len(self._parent.acronym) * 2) + (len(self._parent.acronym) - 1),  # n words with at least 2 characters + spaces
            max_length=50,
        )
        self.add_item(self.answer)
    async def on_submit(self, interaction: discord.Interaction) -> None:
        if interaction.user in self._parent.players:
            await interaction.response.send_message(_("You have already joined this game, with `{answer}` answer.").format(answer=self._parent.players[interaction.user]), ephemeral=True)
            return
        if len(self._parent.players) >= 20:
            await interaction.response.send_message(_("Sorry, maximum 20 players."), ephemeral=True)
            return
        if self._parent._mode != "join":
            await interaction.response.send_message(_("Sorry, the vote has already started."), ephemeral=True)
            return
        answer = self.answer.value.strip()
        if len(answer.split(" ")) != len(self._parent.acronym):
            await interaction.response.send_message(_("Sorry, the number of words in your answer must be {len_words}.").format(len_words=len(self._parent.acronym)), ephemeral=True)
            return
        for i, letter in enumerate(self._parent.acronym):
            if answer.split(" ")[i][0].upper() != letter.upper():
                await interaction.response.send_message(_("Sorry, the initial of each word in your answer must be each letter of the acronym ({acronym}).").format(acronym=self._parent.acronym), ephemeral=True)
                return
        self._parent.players[interaction.user] = answer
        embed: discord.Embed = self._parent._message.embeds[0]
        table = PrettyTable()
	@@ -147,7 +144,7 @@ async def start(self, ctx: commands.Context) -> None:
        )
        table.field_names = ["#", "Name", "Answer", "Votes"]
        for num, (player, answer) in enumerate(players):
            table.add_row([num + 1, (f"{player.display_name[:15]}..." if len(player.display_name) > 15 else player.display_name), answer, self.votes[list(self.players).index(player) + 1]])
        embed: discord.Embed = discord.Embed(
            title="Acronym Game", color=await self.ctx.embed_color()
        )
        embed.description = _("Here is the leaderboard for this game:") + box(str(table), lang='py')
        embed.add_field(name="Random Acronym", value=self.acronym)
        self._message: discord.Message = await self._message.edit(embed=embed, view=self)
        await self._message.reply(_("Winner{s}: {winners}!").format(winners=humanize_list(winners), s="s" if len(winners) > 1 else ""))
        return self._message
    async def on_timeout(self) -> None:
        for child in self.children:
            child: discord.ui.Item
            if hasattr(child, "disabled") and not (isinstance(child, discord.ui.Button) and child.style == discord.ButtonStyle.url):
                child.disabled = True
        try:
            await self._message.edit(view=self)
        except discord.HTTPException:
            pass
    def get_acronym(self) -> str:
        return "".join([random.choice(string.ascii_uppercase) for __ in range(random.choice(range(4, 5)))])
    @discord.ui.button(label="Join Game", emoji="🎮", style=discord.ButtonStyle.success)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        modal = JoinGameModal(self)
        await interaction.response.send_modal(modal)
    async def _callback(
        self, interaction: discord.Interaction, option: discord.SelectOption
    ) -> None:
        if interaction.user in self._voters:
            await interaction.response.send_message(_("You have already voted in this game."), ephemeral=True)
            return
        value = int(option.value)
        if interaction.user == list(self.players)[value - 1]:
            await interaction.response.send_message(_("You can't vote for yourself."), ephemeral=True)
            return
        self._voters[interaction.user] = value
        self.votes[value] += 1
        await interaction.response.send_message(_("Vote given for answer {num}.").format(num=value), ephemeral=True)
