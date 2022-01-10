from db.db import HerokuDatabaseConnector
from db.orm import PostgreORM
from datetime import datetime
import re


class Source:
   def __init__(self, domain: str, news_topics: tuple[str], references: dict[str: str]):
      self.domain = domain
      self.news_topics = news_topics
      self.references = references

   def __setattr__(self, name, value):
      if name == 'domain':
         if type(value) != str:
            raise TypeError('domain must be a string')
         object.__setattr__(self, name, value)
      elif name == 'news_topics':
         if type(value) != tuple:
            raise TypeError('news topics must be a tuple')
         else:
            i = 0
            for v in value:
               if type(v) != str:
                  raise TypeError(f"value '{v}' with index {i} in news topics tuple not a string")
               i += 1
         object.__setattr__(self, name, value)
      elif name == 'references':
         if type(value) != dict:
            raise TypeError('references must be a dictionary')
         else:
            for key, v in value.items():
               if type(key) != str and type(v) != str:
                  raise TypeError(f"references dictionary pair '{key}: {v}' not in str type")
               elif type(key) != str:
                  raise TypeError(f"key '{key}' of references dictionary not a string")
               elif type(v) != str:
                  raise TypeError(f"references dictionary value '{v}' under key '{key}' not a string")
         object.__setattr__(self, name, value)
      else:
         object.__setattr__(self, name, value)
      
   def __str__(self):
      title = "--- Source ---"
      domain = f"Domain: {self.domain}"
      news_topics = f"News topics: {', '.join(self.news_topics)}"
      references = 'References:'
      for news_topic, reference in self.references.items():
         references += f"\n   {news_topic} {reference}"
      return f"{title}\n{domain}\n{news_topics}\n{references}"

   def __repr__(self):
      return f"<{self.domain} | {', '.join(self.news_topics)}>"


class NewsData:
   def __init__(self, id_: str, title: str, url: str, posted: datetime, text: str, intro=None):
      # ID format - "<source_domain>_<source_topic>"
      self.id = id_
      self.title = title
      self.intro = intro
      # Full news URL
      self.url = url
      self.posted = posted
      self.text = text
   
   def __setattr__(self, name, value):
      if name == 'id':
         if type(value) != str:
            raise TypeError('id must be a string')
         spl = value.split('_')
         if len(spl) == 1:
            raise ValueError('id in wrong format, right format is "<source_domain>_<source_topic>"')
         domain_pattern = r'^(([a-z]+\.[a-z]+)+)$'
         topic_pattern = r'^([a-z\-]+)$'
         if not re.match(domain_pattern, spl[0]):
            raise ValueError('domain in id attribute is in the wrong format')
         if not re.match(topic_pattern, spl[1]):
            raise ValueError('topic in id attribute is in the wrong format')
         object.__setattr__(self, name, value)
      elif name in ('title', 'text'):
         if type(value) != str:
            raise TypeError(f"{name} must be a string")
         object.__setattr__(self, name, value)
      elif name == 'url':
         if type(value) != str:
            raise TypeError(f"{name} must be a string")
         url_pattern = r'(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\"\.\, <>?«»“”‘’])|(?: (?<!@)[a-z0-9]+(?: [.\-][a-z0-9]+)*[.](?: com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b /?(?!@ )))'
         if not re.match(url_pattern, value):
            raise ValueError(f"{name} attribute value is in wrong format")
         object.__setattr__(self, name, value)
      elif name == 'posted':
         if type(value) != datetime:
            raise TypeError('posted attribute must have datetime value')
         object.__setattr__(self, name, value)
      else:
         object.__setattr__(self, name, value)

   def get_posted_time(self):
      return self.posted.strftime('%H:%M, %d.%m.%Y')
   
   def __str__(self):
      header = f"--- NewsData {self.id} ---"
      title = f"Title: {self.title}"
      if self.intro:
         intro = f"\nIntro: {self.intro}"
      else:
         intro = ''
      url = f"URL: {self.url}"
      posted = f"Posted datetime: {self.get_posted_time()}"
      return f"{header}\n{title}{intro}\n{url}\n{posted}\n"
   
   def __repr__(self):
      return f"<NewsData {self.id} | {self.title} | {self.get_posted_time()}>"
      

# Connecting to DB and init ORM instance
conn = HerokuDatabaseConnector().connect()
orm = PostgreORM(conn)


# Getting DB data
data = orm.get_sources_references(['sr.source_domain AS domain', 'nt.name AS news_topic', 'sr.url AS url'], 'sr', ['news_topics AS nt ON sr.news_topic_id = nt.id'])

# Structure of this dictionary
# { 'domain': { 'news_topic': 'url' } }
sources_data = {}

# Getting domains and references grouped by news topics
for obj in data:
   if obj.domain not in sources_data:
      sources_data[obj.domain] = {obj.news_topic: obj.url}
   else:
      sources_data[obj.domain][obj.news_topic] = obj.url


# Creating Source class instances
instances = []
for domain in sources_data:
   news_topics = []
   for topic in sources_data[domain]:
      news_topics.append(topic)
   instances.append(
      Source(domain, tuple(news_topics), sources_data[domain])
   )

def search_instance_by_domain(domain):
   global instances
   for instance in instances:
      if instance.domain == domain:
         return instance
