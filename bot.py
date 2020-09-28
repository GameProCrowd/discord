#!/usr/bin/env python3

from typing import Optional

import sys
import random

import discord
import discord.utils
import discord.ext.commands

import db

# Token to use for our bot.
# This is a secret and kept in a seperate file that is never committed.
TOKEN = open('.token', 'r').read().strip()

# Path to database.
DATABASE = "gamepro.db"

# Snowflake of the all mighty one.
GOD = 74755578022334464

# Snowflakes of channels to watch.
CHANNELS = [
  331588982104260608, # General
  241397207226384384, # Offtopic
  572508882316951563  # Super secret testing channel.
]

# Snowflake of our pins channel.
# This is where we archive pinned messages.
PINS = 759688018558189578

# Prefix that denotes command.
PREFIX = '~'

# Whether or not the bot should acknowledge quotes being made.
ACK_ON_QUOTE = True

# Friendly terms used in responses.
TERMS_OF_ENDEARMENT = ['dumbass', 'pal', 'buddy', 'friend', 'idiot', 'nicompoop']

class Bot(discord.Client):
  @property
  def guild(self):
    # We assume presence in only one guild.
    return self.guilds[0]

bot = Bot()

@bot.event
async def on_ready():
  print('Running on Python', sys.version)
  print('Logged on as', bot.user.id, bot.user.name)
  print('Guild is', bot.guild)

_commands = dict()

@bot.event
async def on_message(message):
  if not message.channel.id in CHANNELS:
    # Ignore messages outside of specific channels we care about.
    return

  if message.author.bot:
    # Ignore messages by bots.
    return

  if message.content.startswith(PREFIX):
    # We've got a command.
    parts = message.content.split(' ', 1)
    command = parts[0][1:]
    rest = parts[1] if len(parts) > 1 else None
    if command in _commands:
      # TODO(mtwilliams): Context object.
      handler = _commands[command]
      await handler(message, rest)
    else:
      # Silently swallow unknown commands.
      # We could provide some feedback but that gets too noisy.
      print(f'Unknown command "{command}" issued by {message.author}.')

# TODO(mtwilliams): Decorator to register command.

def register(command, handler, *, help: Optional[str] = None):
  _commands[command] = handler

# Quoting is factored into its own module.
import quotes

async def on_quote_command(context, raw):
  quote = quotes.lookup(raw)
  if quote:
    await context.channel.send(f'> {quote.content}')

register('calc', on_quote_command)

async def on_make_a_quote_command(context, raw):
  try:
    [keyword, content] = raw.split(' ', 1)
  except ValueError:
    # Name and content have to be provided.
    return

  quote = quotes.create(keyword, content, context)

  if ACK_ON_QUOTE:
    # Acknowledge the quote was saved.
    await context.channel.send(f'Saved as #{quote.id}.')

register('mkcalc', on_make_a_quote_command)

async def on_search_for_quote_command(context, raw):
  results = quotes.search([raw])
  if results:
    for result in results:
      await context.channel.send(f'```{result.keyword}: {result.content}```')
  else:
    await context.channel.send(f'No results found, {random.choice(TERMS_OF_ENDEARMENT)}.')

register('apropos', on_search_for_quote_command)

# TODO(mtwilliams): We should prevent people from calling `purge` too often.

async def on_purge_command(context, raw):
  # Caller can provide the number of messages they wish to delete.
  try:
    limit = int(raw)
  except ValueError:
    # Default to one message.
    limit = 1

  # Clamp the provided number to a sane value.
  limit = max(1, min(limit, 100))

  # Note who called this since it's destructive.
  print(f'Deleting {limit} messages from {context.channel} at request of {context.author}.')
  await context.channel.purge(limit=limit)

register('purge', on_purge_command, help='Deletes some number of messages.')

# Setup our database.
db.setup(DATABASE)

# Run our bot until the end of time.
# This will use the default asynchronous loop.
bot.run(TOKEN)
