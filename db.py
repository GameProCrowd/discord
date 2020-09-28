"""Local database used by our bot."""

import datetime

import peewee
from peewee import AutoField, IntegerField, BigIntegerField, TextField, DateTimeField
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.sqlite_ext import JSONField

# We connect to our database dynamically.
_proxy: peewee.DatabaseProxy = peewee.DatabaseProxy()

class Model(peewee.Model):
  class Meta:
    database = _proxy

class Message(Model):
  """Archived message."""

  class Meta:
    # These are copies of our messages and so they are stored under a more descriptive table name.
    table_name = 'history'

  # Snowflake assigned by Discord.
  id = BigIntegerField(primary_key=True)

  # Link to jump to message.
  link = TextField()

  # Author of message.
  author = BigIntegerField()

  # Cached information about the author.
  # See `author_to_cacheable` for contents.
  _cached_author_info = JSONField()

  # Channel in which the message was posted.
  channel = BigIntegerField()

  # Cached information about the channel.
  # See `channel_to_cacheable` for contents.
  _cached_channel_info = JSONField()

  # Content of message.
  content = TextField()

  # Reactions to message.
  # See `reaction_to_cacheable` for contents.
  reactions = JSONField()

  # Timestamp when message was posted.
  timestamp = DateTimeField()

class Quote(Model):
  """Arbitrary quotes that can be referenced by keyword."""

  class Meta:
    # Historically these were called "calcs" due to bot responsible for them.
    # Also because Mykola didn't understand English.
    table_name = 'quotes'

  # Auto increment idenitifer.
  id = AutoField(primary_key=True)

  # Author of the quote.
  author = BigIntegerField()

  # Keyword associated with the quote.
  keyword = TextField()

  # Free form content comprising the quote.
  content = TextField()

  # Link to jump to message that originated the quote.
  link = TextField()

  # Timestamp when the quote was created.
  # We use `utcnow` rather than `now(timezone.utc)` because timezones screw up SQlite3.
  timestamp = DateTimeField(default=datetime.datetime.utcnow)

def setup(path: str):
  db = SqliteExtDatabase(path)

  # Ensure foreign key and constraints are enforced.
  db.pragma('foreign_keys', 1, permanent=True)
  db.pragma('ignore_check_constraints', 0, permanent=True)

  # Bind to database.
  _proxy.initialize(db)
