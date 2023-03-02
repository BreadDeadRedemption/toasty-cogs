import asyncio
import discord
from redbot.core import commands
from redbot.core import checks
from redbot.core import Config

class AutoDeleter(commands.Cog):
    """Automatically deletes messages that match certain criteria."""
    def __init__(self, bot):
        self.bot = bot
        self.deletion_tasks = {}
        self.config = Config.get_conf(self, identifier=123456789)
        self.config.register_guild(rules={})

    async def delete_message(self, message_id, delay):
        await asyncio.sleep(delay)
        try:
            message = await self.bot.get_channel(message.channel.id).fetch_message(message_id)
            await message.delete()
        except:
            pass
        finally:
            del self.deletion_tasks[message_id]

    @commands.group(name='autodeleter', aliases=['ad'], brief='Automatically deletes messages that match certain criteria.')
    @checks.admin()
    async def autodeleter(self, ctx):
        """
        Group command for managing autodeletion rules.

        Commands:
        - new: Creates a new rule.
        - delete: Deletes an existing rule.
        - apply: Applies a rule to a channel or thread.
        - edit: Edits an existing rule.
        - list: Lists all existing rules.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    @autodeleter.command(name='new', brief='Creates a new rule.')
    async def new_rule(self, ctx, rule_name, content_type, delay, *, targets=''):
        """
        Creates a new autodeletion rule.

        Parameters:
        - rule_name: The name of the new rule.
        - content_type: The type of content to be deleted (e.g. "images", "links", "text", etc.).
        - delay: The time delay before the message is deleted, in seconds, minutes, hours, or days.
        - targets (optional): The users or roles to which the rule should apply (defaults to everyone).
        """
        rule_name = rule_name.lower()
        content_type = content_type.lower()
        targets = targets.split(',')
        targets = [t.strip() for t in targets]
        delay = self.parse_delay(delay)
        if delay is None:
            await ctx.send('Invalid delay format. Please use the format "1s", "1m", "1h", "1d", or "1w".')
            return

        if rule_name in await self.config.guild(ctx.guild).rules():
            await ctx.send(f'Rule "{rule_name}" already exists.')
            return

        rule_data = {
            'content_type': content_type,
            'delay': delay,
            'targets': targets,
            'applied_channels': []
        }
        rules = await self.config.guild(ctx.guild).rules()
        rules[rule_name] = rule_data
        await self.config.guild(ctx.guild).rules.set(rules)
        await ctx.send(f'Rule "{rule_name}" created successfully.')

    @autodeleter.command(name='delete', brief='Deletes an existing rule.')
    async def delete_rule(self, ctx, rule_name):
        """
        Deletes an existing autodeletion rule.

        Parameters:
        - rule_name: The name of the rule to delete.
        """
        rule_name = rule_name.lower()
        rules = await self.config.guild(ctx.guild).rules()
        if rule_name not in rules:
            await ctx.send(f'Rule "{rule_name}" not found.')
            return

        del rules[rule_name]
        await self.config.guild
        (ctx.guild).rules.set(rules)
        await ctx.send(f'Rule "{rule_name}" deleted successfully.')

    @autodeleter.command(name='apply', brief='Applies a rule to a channel or thread.')
    async def apply_rule(self, ctx, rule_name, channel: discord.TextChannel):
        """
        Applies a rule to a channel or thread.

        Parameters:
        - rule_name: The name of the rule to apply.
        - channel: The channel or thread to which the rule should be applied.
        """
        rule_name = rule_name.lower()
        rules = await self.config.guild(ctx.guild).rules()
        if rule_name not in rules:
            await ctx.send(f'Rule "{rule_name}" not found.')
            return

        rule_data = rules[rule_name]
        if channel.id in rule_data['applied_channels']:
            await ctx.send(f'Rule "{rule_name}" already applied to {channel.mention}.')
            return

        rule_data['applied_channels'].append(channel.id)
        rules[rule_name] = rule_data
        await self.config.guild(ctx.guild).rules.set(rules)
        await ctx.send(f'Rule "{rule_name}" applied to {channel.mention} successfully.')
        value+= f'Targets: {targets}\n'
        embed.add_field(name='\u200b', value='\u200b', inline=False)

        await ctx.send(embed=embed)

def parse_delay(self, delay_str):
    """
    Parses a delay string and returns the equivalent number of seconds.

    Parameters:
    - delay_str: The delay string to parse.

    Returns:
    - The number of seconds corresponding to the delay string, or None if the string is invalid.
    """
    try:
        delay = 0
        units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800
        }
        for unit in units:
            if unit in delay_str:
                num_str = delay_str.split(unit)[0]
                num = int(num_str)
                delay += num * units[unit]
                delay_str = delay_str.replace(num_str + unit, '')
        return delay
    except:
        return None

def format_delay(self, delay):
    """
    Formats a delay value in seconds as a string.

    Parameters:
    - delay: The delay value in seconds.

    Returns:
    - A string representation of the delay value.
    """
    if delay >= 604800:
        return f'{int(delay / 604800)}w'
    elif delay >= 86400:
        return f'{int(delay / 86400)}d'
    elif delay >= 3600:
        return f'{int(delay / 3600)}h'
    elif delay >= 60:
        return f'{int(delay / 60)}m'
    else:
        return f'{delay}s'


    @autodeleter.command(name='edit', brief='Edits an existing rule.')
    async def edit_rule(self, ctx, rule_name, content_type='', delay='', targets=''):
        """
        Edits an existing autodeletion rule.

        Parameters:
        - rule_name: The name of the rule to edit.
        - content_type (optional): The new type of content to be deleted.
        - delay (optional): The new time delay before the message is deleted.
        - targets (optional): The new users or roles to which the rule should apply.
        """
        rule_name = rule_name.lower()
        rules = await self.config.guild(ctx.guild).rules()
        if rule_name not in rules:
            await ctx.send(f'Rule "{rule_name}" not found.')
            return

            rule_data = rules[rule_name]
            if content_type:
                rule_data['content_type'] = content_type.lower()
            if delay:
                delay = self.parse_delay(delay)
                if delay is None:
                    await ctx.send('Invalid delay format. Please use the format "1s", "1m", "1h", "1d", or "1w".')
                    return
                rule_data['delay'] = delay
            if targets:
                targets = targets.split(',')
                targets = [t.strip() for t in targets]
                rule_data['targets'] = targets

            rules[rule_name] = rule_data
            await self.config.guild(ctx.guild).rules.set(rules)
            await ctx.send(f'Rule "{rule_name}" edited successfully.')

    @autodeleter.command(name='list', brief='Lists all existing rules.')
    async def list_rules(self, ctx):
        """
        Lists all existing autodeletion rules.
        """
        rules = await self.config.guild(ctx.guild).rules()
        if not rules:
            await ctx.send('No rules found.')
            return

        embed = discord.Embed(title='Autodeletion Rules', color=discord.Color.blue())
        for rule_name, rule_data in rules.items():
            channel_mentions = [ctx.guild.get_channel(c).mention for c in rule_data['applied_channels']]
            if not channel_mentions:
                channel_mentions = ['No channels specified']
            content_type = rule_data['content_type']
            delay = self.format_delay(rule_data['delay'])
            targets = ', '.join(rule_data['targets']) or 'Everyone'
            embed.add_field(name=rule_name, value=f'Channels: {", ".join(channel_mentions)}\nContent type: {content_type}\nDelay: {delay}\nTargets: {targets}\n', inline=False)
            value+= f'Targets: {targets}\n'
            embed.add_field(name='\u200b', value='\u200b', inline=False)

        await ctx.send(embed=embed)

def parse_delay(self, delay_str):
    """
    Parses a delay string and returns the equivalent number of seconds.

    Parameters:
    - delay_str: The delay string to parse.

    Returns:
    - The number of seconds corresponding to the delay string, or None if the string is invalid.
    """
    try:
        delay = 0
        units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800
        }
        for unit in units:
            if unit in delay_str:
                num_str = delay_str.split(unit)[0]
                num = int(num_str)
                delay += num * units[unit]
                delay_str = delay_str.replace(num_str + unit, '')
        return delay
    except:
        return None

def format_delay(self, delay):
    """
    Formats a delay value in seconds as a string.

    Parameters:
    - delay: The delay value in seconds.

    Returns:
    - A string representation of the delay value.
    """
    if delay >= 604800:
        return f'{int(delay / 604800)}w'
    elif delay >= 86400:
        return f'{int(delay / 86400)}d'
    elif delay >= 3600:
        return f'{int(delay / 3600)}h'
    elif delay >= 60:
        return f'{int(delay / 60)}m'
    else:
        return f'{delay}s'

