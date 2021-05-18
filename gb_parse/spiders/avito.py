import scrapy
from ..loaders import AvitoLoader


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["avito.ru"]
    start_urls = ["https://www.avito.ru/vladivostok/kvartiry/prodam-ASgBAgICAUSSA8YQ"]

    _xpath_selectors = {

        "pagination": "//span[contains(@data-marker, 'page')]/@data-marker",

        "flat": "//div[@class='iva-item-titleStep-2bjuh']//a[@class='link-link-39EVK link-design-default-2sPEv" 
                "title-root-395AQ iva-item-title-1Rmmj title-listRedesign-3RaU2 title-root_maxHeight-3obWc']/@href",

    }

    _xpath_data_selectors = (

        {"field_name": "title", "xpath": "//span[@class='title-info-title-text']/text()"},

        {"field_name": "price", "xpath": "//span[@class='js-item-price']/text()"},

        {
            "field_name": "adress",
            "xpath": "//span[@class='item-address__string']/text()",
        },

        {
            "field_name": "characteristics",
            "xpath": "//li[@class='item-params-list-item']//text()",
        },

        {
            "field_name": "author_name",
            "xpath": "//div[@class='seller-info-name js-seller-info-name']//text()"
        },

        {
            "field_name": "author_link",
            "xpath": "//div[@class='seller-info-name js-seller-info-name']//@href"
        },

    )

    def _get_follow(self, response, selector_str, callback):
        for url in response.xpath(selector_str):
            yield response.follow(url, callback=callback)

    def pagination_parse(self, response, selector_str, callback):
        pages = len(response.xpath(selector_str)) - 1
        for i in range(pages):
            p = f'?p={i+1}'
            a = self.start_urls[0]
            url_pagination = a + p
            yield response.follow(url_pagination, callback=callback)


    def parse(self, response):
        yield from self.pagination_parse(
            response,
            self._xpath_selectors["pagination"],
            self.parse
        )
        yield from self._get_follow(
            response,
            self._xpath_selectors["flat"],
            self.flat_parse,
        )

    def flat_parse(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for xpath_strict in self._xpath_data_selectors:
            loader.add_xpath(**xpath_strict)
        yield loader.load_item()