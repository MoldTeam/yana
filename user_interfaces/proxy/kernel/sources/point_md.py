from sources import search_instance_by_domain, NewsData
import requests
import json
from datetime import datetime
from parsing_functions import get_news_text


POINT_MD = search_instance_by_domain('point.md')


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


def _get_society_news(source=POINT_MD):
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
      news_url = url + '/' + news['url'] + '/'
      # Create NewsData instance
      obj = NewsData(
          'point.md_society',
          news['title']['short'],
          news_url,
          datetime(
              int(news['dates']['postedSeparator'][-4:]),
              _get_month_count(news['dates']['postedDM'].split(' ')[1]),
              int(news['dates']['postedDM'].split(' ')[0]),
              int(news['dates']['postedH'].split(':')[0]),
              int(news['dates']['postedH'].split(':')[1])
          ),
          get_news_text(news_url, {'id': 'article-content'}),
          news['description']['intro']
      )
      objects.append(obj)
   return objects

POINT_MD.get_society_news = _get_society_news


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


def _get_news_data(news_topic: str, start_key: str, end_key: str, source=point_md):
   url = source.references[news_topic]
   res = requests.get(url)
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
      news_url = url + news['url'] + '/'
      obj = NewsData(
          f'point.md_{news_topic}',
          news['title']['short'],
          news_url,
          datetime(
              int(news['dates'][date_key][-4:]),
              _get_month_count(news['dates'][date_key].split(' ')[1]),
              int(news['dates'][date_key][:2]),
              int(news['dates'][time_key].split(':')[0]),
              int(news['dates'][time_key].split(':')[1])
          ),
          get_news_text(news_url, {'id': 'article-content'}),
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

POINT_MD.get_economy_news = _get_economy_news


def _get_sport_news():
   return _get_news_data(
       'sport',
       '"cparent":{"__ref":"Topic:ee890be5-3d93-41bb-bcf4-2c1074d965f3"},"poll_id":""},',
       ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

POINT_MD.get_sport_news = _get_sport_news


def _get_world_news():
   return _get_news_data(
       'world',
       '"cparent":{"__ref":"Topic:40c82eac-8c85-4c42-bf60-3f68701108ec"},"poll_id":""},',
       ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

POINT_MD.get_world_news = _get_world_news


def _get_hi_tech_news():
   return _get_news_data(
       'hi-tech',
       ',"cparent":{"__ref":"Topic:d71df14f-ed8f-4ab9-9969-4a96948bd937"},"poll_id":""},',
       ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

POINT_MD.get_hi_tech_news = _get_hi_tech_news


def _get_politics_news():
   return _get_news_data(
       'politics',
       ',"cparent":{"__ref":"Topic:689b93b0-acdc-43db-8e8f-40c207613e0a"},"poll_id":""},',
       ',"ROOT_QUERY":{"__typename":"Query","topics({\\"lang\\":\\"ru\\",\\"project_id\\":\\"5107de83-f208-4ca4-87ed-9b69d58d16e1\\"'
   )

POINT_MD.get_politics_news = _get_politics_news
