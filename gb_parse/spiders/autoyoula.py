import scrapy
import pymongo

import re

class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    data_query = {
        "url": lambda resp: resp.url,
        "title": lambda resp: resp.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
        "images": lambda resp: resp.css(
            "figure.PhotoGallery_photo__36e_r img.PhotoGallery_photoImage__2mHGn::attr('src')").getall(),
        "характеристики": lambda resp: [
            {
                "name": resp.css(".AdvertSpecs_label__2JHnS::text").extract_first(),
                "value": resp.css(".AdvertSpecs_data__xK2Qx::text").extract_first()
                        or resp.css(".AdvertSpecs_data__xK2Qx a::text").extract_first(),
            }
        ],
        "Описание авто": lambda resp: resp.css(
            "div.AdvertCard_description__2bVlR div.AdvertCard_descriptionWrap__17EU3 div.AdvertCard_descriptionInner__KnuRi::text").get(),
        "автор": lambda resp: AutoyoulaSpider.authot_id(resp),

    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector, callback): #создается для того, чтобы выполнять похожую операцию в следующих двух ф-циях
        for itm in response.css(selector):
            url = itm.attrib["href"]
            yield response.follow(url, callback=callback) #callback - ф-ция

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            "div.TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink", #то, по чему выбираешь, селектор
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response,
            "div.Paginator_block__2XAPy a.Paginator_button__u1e7D", #обработка ссылок пагинаций
            self.brand_parse,
        )

        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu", #ссылки на сами страницы объявлений
            self.car_parse,
        )

    def car_parse(self, response): #работа уже с самими объявлениями
        #print(1)
        data = {}
        for key, selector in self.data_query.items():
            try:
                data[key] = selector(response)
            except (ValueError, AttributeError):
                continue
        self.db_client["parse"][self.name].insert_one(data)

    @staticmethod
    def authot_id(resp):
        marker = "window.transitState = decodeURIComponent"
        for script in resp.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%C%22([a-zA-Z|\d]+)%22%2C%%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (
                        resp.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass