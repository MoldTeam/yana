from db import HerokuDatabaseConnector
from orm import PostgreORM
import requests
import json
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
   def __init__(self, id_: str, title: str, url: str, posted: datetime, intro=None):
      # ID format - "<source_domain>_<source_topic>"
      self.id = id_
      self.title = title
      self.intro = intro
      # Full news URL
      self.url = url
      self.posted = posted
   
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
      elif name == 'title':
         if type(value) != str:
            raise TypeError("title must be a string")
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

def _search_instance_by_domain(domain):
   global instances
   for instance in instances:
      if instance.domain == domain:
         return instance


# In this list are all modified instances with methods added to them
modified_instances = []


instance = _search_instance_by_domain('point.md')

def _get_month_count(month: str) -> int:
   if type(month) != str:
      raise TypeError('month must be a string')
   if month in ('January', 'Jan', 'Январь', 'Января', 'Янв'):
      return 1
   elif month in ('February', 'Feb', 'Февраль', 'Февраля', 'Фев'):
      return 2
   elif month in ('March', 'Mar', 'Март', 'Марта', 'Мар'):
      return 3
   elif month in ('April', 'Apr', 'Апрель', 'Апреля', 'Апр'):
      return 4
   elif month in ('May', 'Май', 'Мая'):
      return 5
   elif month in ('June', 'Jun', 'Июнь', 'Июня', 'Июн'):
      return 6
   elif month in ('July', 'Jul', 'Июль', 'Июля', 'Июл'):
      return 7
   elif month in ('August', 'Aug', 'Август', 'Августа', 'Авг'):
      return 8
   elif month in ('September', 'Sep', 'Sept', 'Сентябрь', 'Сентября', 'Сен'):
      return 9
   elif month in ('Octomber', 'Oct', 'Октябрь', 'Октября', 'Окт'):
      return 10
   elif month in ('November', 'Nov', 'Ноябрь', 'Ноября', 'Ноя'):
      return 11
   elif month in ('December', 'Dec', 'Декабрь', 'Декабря', 'Дек'):
      return 12
   else:
      raise ValueError('unknown month')


def _get_society_news(source=instance):
   url = source.references['society']
   res = requests.get(url)
   start_key_str = '"cparent":{"__typename":"Topic","id":"864bac82-c489-4e4b-a66f-4e6da7f8c1d1","title":{"__typename":"MultilangString","ru":"Общество"},"url":{"__typename":"MultilangString","ru":"obschestvo"},"type":"category"},"pollId":""}],"contents":['
   end_key_str = ']},"notFound":false,"categoryUrl":"obschestvo","selectedTopic":{"__typename":"Topic","id":"864bac82-c489-4e4b-a66f-4e6da7f8c1d1","title":{"__typename":"MultilangString","ru":"Общество"}'
   # News data element structure
   '''
      {
         "__typename":"Content",
         "id":"<content_id>",
         "title":{
            "__typename":"ContentTitle",
            "short":"<short_title_ru>",
            "long":"<long_title_ru>"
         },
         "url":"<news_url>",
         "description":{
            "__typename":"ContentDescription",
            "intro":"<news_intro>"
         },
         "dates":{
            "__typename":"ContentDates",
            "posted":"<news_posted_date_or_time>",
            "postedWithYear":"<DD MM_short. YYYY hh:mm>",
            "postedSeparator":"<DD MM_short YYYY>",
            "postedTs":"<number>",
            "postedH":"hh:mm",
            "postedDM":"DD MM_full",
            "dateT":"<news_posted_time>"
         },
         "counters":{
            "__typename":"Counters",
            "comment":"<number_of_comments>",
            "view":"<number_of_views>",
            "like":"<number_of_likes>"
         },
         "thumbnail":"<news_image_file_name>",
         "tags":["<tag_1>","<tag_..>","<tag_n>"],
         "cparent":{
            "__typename":"Topic",
            "id":"<topic_id>",
            "title":{
               "__typename":"MultilangString",
               "ru":"Общество"
            },
            "url":{
               "__typename":"MultilangString",
               "ru":"obschestvo"
            },
            "type":"category"
         },
         "pollId":""
      }
   '''
   def get_news_data(response_text=res.text, start_key_string=start_key_str, end_key_string=end_key_str):
      # Getting news data string
      start_index = response_text.find(start_key_string)
      content_index = start_index + len(start_key_string)
      news_data = response_text[content_index:]
      end_index = news_data.find(end_key_string)
      news_data = news_data[:end_index]
      news_data = '{' + news_data + '}'
      # Getting news strings
      news = []
      brackets = 0
      element = ''
      n = 0
      for char in ('{' + news_data.strip('{}') + '}'):
         element += char
         if char == '}' and brackets < 7:
            brackets += 1
         elif char == '}' and brackets == 7:
            brackets = 0
            n += 1
            element = f'"NewsData {n}":' + element.lstrip(',')
            news.append(element)
            element = ''
      # Return news data elements dictionary
      return json.loads('{' + ', '.join(news) + '}')
   # Creating and return news data objects
   news_data = get_news_data()
   objects = []
   for key in news_data:
      news = news_data[key]
      obj = NewsData(
         'point.md_society',
         news['title']['short'],
         instance.references['society'] + news['url'] + '/',
         datetime(
            int(news['dates']['postedSeparator'][-4:]),
            _get_month_count(news['dates']['postedDM'].split(' ')[1]),
            int(news['dates']['postedDM'].split(' ')[0]),
            news['dates']['postedH'].split(':')[0],
            news['dates']['postedH'].split(':')[1]
         ),
         news['description']['intro']
      )
      objects.append(obj)
   return objects

instance.get_society_news = _get_society_news


# This function only works with news data elements for point.md that have the following structure
'''
   "Content:<id>":{
      "id":"<content_id>",
      "__typename":"Content",
      "title":{
         "__typename":"ContentTitle",
         "short":"<short_title>",
         "long":"<long_title>"
      },
      "url":"<news_url>",
      "description":{
         "__typename":"ContentDescription",
         "intro":"<news_intro>"
      },
      "dates":{
         "__typename":"ContentDates",
         "posted({\"format\":\"2 $$Jan$$. 15:04\",\"getDiff\":true,\"lang\":\"ru\"})":"<news_posted_date_or_time>",
         "posted({\"format\":\"2 $$Jan$$. 2006 15:04\",\"lang\":\"ru\"})":"<DD MM_short YYYY hh:mm>,
         "posted({\"format\":\"2 $$Jan$$. 2006\",\"lang\":\"ru\"})":"<DD MM_short YYYY>",
         "posted":"<number>",
         "posted({\"format\":\"15:04\",\"lang\":\"ru\"})":"<hh:mm>",
         "posted({\"format\":\"2 $$January$$\",\"lang\":\"ru\"})":"<DD MM_full>",
         "posted({\"getDiff\":true,\"lang\":\"ru\"})":"<news_posted_date_or_time>"
      },
      "counters":{
         "__typename":"Counters",
         "comment":"<comments_count>",
         "view":"<views_count>",
         "like":"<likes_count>"
      },
      "thumbnail":"<news_image_file_name>",
      "tags":["<tag_1>","<tag_..>","<tag_n>"],
      "cparent":{
         "__ref":"Topic:dc6b8b58-52e2-4e0e-a908-0cc44c985030"
      },
      "poll_id":""
   }
'''
def _get_news_data(news_topic: str, start_key: str, end_key: str, source=instance):
   url = source.references[news_topic]
   res = requests.get(url)
   # print(res.text)
   # Getting indexes
   start_index = res.text.find(start_key) + len(start_key)
   end_index = res.text.find(end_key)
   # Getting news data
   data_str = "{" + res.text[start_index:end_index] + "}"
   news_data = json.loads(data_str)
   date_key = 'posted({"format":"2 $$Jan$$ 2006","lang":"ru"})'
   time_key = 'posted({"format":"15:04","lang":"ru"})'
   objects = []
   for key in news_data:
      news = news_data[key]
      obj = NewsData(
         f'point.md_{news_topic}',
         news['title']['short'],
         url + news['url'] + '/',
         datetime(
            int(news['dates'][date_key][-4:]),
            _get_month_count(news['dates'][date_key].split(' ')[1]),
            int(news['dates'][date_key][:2]),
            int(news['dates'][time_key].split(':')[0]),
            int(news['dates'][time_key].split(':')[1])
         ),
         news['description']['intro']
      )
      objects.append(obj)
   return objects


def _get_economy_news():
   return _get_news_data(
      'economy',
      '"cparent":{"__ref":"Topic:dc6b8b58-52e2-4e0e-a908-0cc44c985030"},"poll_id":""},',
      ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

instance.get_economy_news = _get_economy_news


def _get_sport_news():
   return _get_news_data(
      'sport',
      '"cparent":{"__ref":"Topic:ee890be5-3d93-41bb-bcf4-2c1074d965f3"},"poll_id":""},',
      ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

instance.get_sport_news = _get_sport_news


def _get_world_news():
   return _get_news_data(
      'world',
      '"cparent":{"__ref":"Topic:40c82eac-8c85-4c42-bf60-3f68701108ec"},"poll_id":""},',
      ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

instance.get_world_news = _get_world_news


def _get_hi_tech_news():
   return _get_news_data(
      'hi-tech',
      ',"cparent":{"__ref":"Topic:d71df14f-ed8f-4ab9-9969-4a96948bd937"},"poll_id":""},',
      ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

instance.get_hi_tech_news = _get_hi_tech_news


def _get_politics_news():
   return _get_news_data(
      'politics',
      ',"cparent":{"__ref":"Topic:689b93b0-acdc-43db-8e8f-40c207613e0a"},"poll_id":""},',
      ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

instance.get_politics_news = _get_politics_news


modified_instances.append(instance)
