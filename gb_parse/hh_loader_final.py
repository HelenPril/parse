#предоставляют интерфейс для потокового извлечения данных из респонса
from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose

#TakeFirst - выборка первого ЗНАЧЕНИЯ из списка, встроенная ф-ция

def flat_text(items):
    return "\n".join(items)

def hh_user_url(user_id):
    return urljoin("https://hh.ru/", user_id)


class HhLoader(ItemLoader):
    default_item_class = dict  #какой тип айтем будет на выходе
    url_out = TakeFirst() #out - то, что вернется, будет в результирующем словаре, который мы объявили
    title_out = TakeFirst()
    salary_out = flat_text
    description_out = flat_text
    author_link_in = MapCompose(hh_user_url)
    author_link_out = TakeFirst()
    employer_out = TakeFirst()
    employer_link_out = TakeFirst()
    com_description_out = flat_text


