from sources import NewsData, search_instance_by_domain
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from parsing_functions import get_news_text


VEDOMOSTI_MD = search_instance_by_domain('vedomosti.md')


def _get_news_data(topic: str, source=VEDOMOSTI_MD):
   url = source.references[topic]
   res = requests.get(url)
   soup = BeautifulSoup(res.text, 'html.parser')
   news_elem = soup.find('ul', class_='list-news')
   news_list = news_elem.find_all('li')
   objects = []
   for news in news_list:
      divs = news.find_all('div')
      news_date = divs[0].get_text().split('.')
      # Getting url and title
      strong = divs[1].find('strong')
      a = strong.find('a')
      news_title = a.get_text()
      news_url = 'http://vedomosti.md' + a['href']
      # Getting intro
      intro_elem = divs[2].find('span')
      if intro_elem is None:
         intro_elem = divs[2].find('p')
      try:
         news_intro = intro_elem.text
      except AttributeError:
         news_intro = divs[2].text
      news_intro = news_intro.strip()
      # Create NewsData instance
      obj = NewsData(
          f'vedomosti.md_{topic}',
          news_title,
          news_url,
          datetime(
              int(news_date[2]),
              int(news_date[1]),
              int(news_date[0])
          ),
          get_news_text(news_url, {'class': 'article-content'}),
          news_intro
      )
      objects.append(obj)


def _get_politics_news():
   return _get_news_data('politics')

VEDOMOSTI_MD.get_politics_news = _get_politics_news


def _get_society_news():
   return _get_news_data('society')

VEDOMOSTI_MD.get_society_news = _get_society_news


def _get_economy_news():
   return _get_news_data('economy')

VEDOMOSTI_MD.get_economy_news = _get_economy_news


def _get_sport_news():
   return _get_news_data('sport')

VEDOMOSTI_MD.get_sport_news = _get_sport_news
