from sources import search_instance_by_domain, NewsData
import requests
from bs4 import BeautifulSoup
from datetime import datetime


NOVOSTIPMR_COM = search_instance_by_domain('novostipmr.com')


def _get_news_data(topic: str, source=NOVOSTIPMR_COM):
    url = source.references[topic]
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    # Getting news data elements
    news_elem = soup.find('section', {'id': 'block-system-main'})
    news_data = news_elem.find_all('div', {'class': ['node', 'node-article']})
    # Getting news data and creating objects
    objects = []
    for news in news_data:
        data = news.find('div', class_='wr-info')
        dt = data.find('div', class_='teaser-date').text.split(' ')
        date = dt[0].split('/')
        time = dt[1].split(':')
        title_elem = data.find('div', class_='teaser-title').find('h2').find('a')
        news_url = 'https://novostipmr.com' + title_elem['href']
        # Getting news text
        news_res = requests.get(news_url)
        news_soup = BeautifulSoup(news_res.text, 'html.parser')
        paragraphs = news_soup.find('div', class_='field-type-text-with-summary').find('div', class_='field-items').find('div', class_='field-item').find_all('p')
        news_text = ''
        for p in paragraphs:
            strong = p.find('strong')
            if strong:
                news_text += p.text.replace(strong.text, '')
            else:
                news_text += p.text
            news_text += ' '
        news_title = title_elem.text
        news_intro = data.find('div', 'teaser-body').find('div', class_='field').find('div', class_='field-items').find('div', class_='field-item').text
        # Creating object
        obj = NewsData(
            f'novostipmr.com_{topic}',
            news_title,
            news_url,
            datetime(
                int('20' + date[2]),
                int(date[1]),
                int(date[0]),
                int(time[0]),
                int(time[1])
            ),
            news_text,
            news_intro
        )
        objects.append(obj)
    return objects


def _get_culture_news():
    return _get_news_data('culture')

NOVOSTIPMR_COM.get_culture_news = _get_culture_news


def _get_politics_news():
    return _get_news_data('politics')

NOVOSTIPMR_COM.get_politics_news = _get_politics_news


def _get_economy_news():
    return _get_news_data('economy')

NOVOSTIPMR_COM.get_economy_news = _get_economy_news


def _get_society_news():
    return _get_news_data('society')

NOVOSTIPMR_COM.get_society_news = _get_society_news
