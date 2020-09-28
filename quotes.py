from typing import List
from typing import Optional

from db import Quote

def create(keyword: str, content: str, context) -> Quote:
  author = context.author
  quote = Quote.create(author=author.id, keyword=keyword, content=content, link=str(context.jump_url))
  return quote

def lookup(keyword: str) -> Optional[Quote]:
  try:
    # Find the newest version of a quote by keyword.
    return Quote.select().where(Quote.keyword == keyword).order_by(Quote.timestamp.desc()).get()
  except Quote.DoesNotExist:
    # No such quote.
    pass

# TODO(mtwilliams): Squash into one version only.
# TODO(mtwilliams): Support multiple keywords.
def search(keywords: List[str], limit: int = 3) -> List[Quote]:
  keyword = keywords[0]
  quotes = Quote.select().where(Quote.keyword.contains(keyword) or Quote.content.contains(keyword)).order_by(Quote.timestamp.desc()).limit(limit).execute()
  return quotes
