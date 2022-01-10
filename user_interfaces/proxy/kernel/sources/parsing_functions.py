import requests
from bs4 import BeautifulSoup


def get_news_text(url: str, attrs: dict[str: str], tag_name='div', exclude_elems=[], check_child_for_exclude=True, strip_duplicated=True) -> str:
   res = requests.get(url)
   soup = BeautifulSoup(res.text, 'html.parser')
   text_elem = soup.find(tag_name, attrs)
   elems = text_elem.find_all()
   exclude_elems = exclude_elems + ['a']
   previous_text = None
   text = ''
   for elem in elems:
      if elem.name not in exclude_elems:
         if check_child_for_exclude:
            child_elems = elem.find_all()
            exists_exclude_elem = False
            for el in child_elems:
               if el.name in exclude_elems:
                  exists_exclude_elem = True
            if not exists_exclude_elem:
               if strip_duplicated and elem.text != previous_text:
                  text += elem.text
         elif strip_duplicated and elem.text != previous_text:
            text += elem.text
         previous_text = elem.text
   return text
