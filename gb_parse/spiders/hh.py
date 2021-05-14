import scrapy
from ..hh_loader import HhLoader


class HhSpider(scrapy.Spider):
    name = "hh"
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113/"]
    _xpath_selectors = {
        "pagination": "//div[@data-qa='pager-block']//a[@class='bloko-button']/@href",
        "job": "//div[contains(@class, 'vacancy-serp-item')]//a[@class='bloko-link']/@href",
    }
    _xpath_data_selectors = (
        {"field_name": "title", "xpath": "//h1[@data-qa='vacancy-title']/text()"},
        {"field_name": "salary", "xpath": "//p[@class='vacancy-salary']//text()"},
        {
            "field_name": "skills",
            "xpath": "//div[contains(@class,'bloko-tag')]//text()",
        },
        {
            "field_name": "description",
            "xpath": "//div[@class='vacancy-description']//text()",
        },
        {
            "field_name": "author_name",
            "xpath": "//span[@class='bloko-section-header-2 bloko-section-header-2_lite']//text()",
        },
        {
            "field_name": "author_link",
            "xpath": "//a[@class='vacancy-company-name']/@href",
        },
    )

    def _get_follow(self, response, selector_str, callback):
        for url in response.xpath(selector_str):
            yield response.follow(url, callback=callback)


    def parse(self, response):
        yield from self._get_follow(
            response,
            self._xpath_selectors["pagination"],
            self.parse
        )
        yield from self._get_follow(
            response,
            self._xpath_selectors["job"],
            self.job_parse,
        )

    def job_parse(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        for xpath_strict in self._xpath_data_selectors:
            loader.add_xpath(**xpath_strict)
        yield loader.load_item()