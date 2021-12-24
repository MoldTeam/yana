class Source:
   def __init__(self, domain: str, news_topics: tuple[str], references: dict[str: str]):
      self.domain = domain
      self.news_topics = news_topics
      self.references = references

   def __setattr__(self, name, value):
      if name == 'domain':
         if type(domain) != str:
            raise TypeError('domain must be a string')
         object.__setattr__(self, name, value)
      elif name == 'news_topics':
         if type(news_topics) != tuple:
            raise TypeError('news topics must be a tuple')
         else:
            i = 0
            for value in news_topics:
               if type(value) != str:
                  raise TypeError(f"value '{value}' with index {i} in news topics tuple not a string")
               i += 1
      elif name == 'references':
         if type(references) != dict:
            raise TypeError('references must be a dictionary')
         else:
            for key, value in references.items():
               if type(key) != str and type(value) != str:
                  raise TypeError(f"references dictionary pair '{key}: {value}' not in str type")
               elif type(key) != str:
                  raise TypeError(f"key '{key}' of references dictionary not a string")
               elif type(value) != str:
                  raise TypeError(f"references dictionary value '{value}' under key '{key}' not a string")
