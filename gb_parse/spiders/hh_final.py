import scrapy
from ..hh_loader_final import HhLoader


class HhSpider(scrapy.Spider):
    name = "hh"
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113/"]
    _xpath_selectors = {
        "pagination": "//div[@data-qa='pager-block']//a[@class='bloko-button']/@href",
        "job": "//div[contains(@class, 'vacancy-serp-item')]//a[@class='bloko-link']/@href",
        "employer": "//a[@data-qa='vacancy-serp__vacancy-employer-logo']/@href"
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

    _xpath_employer_selectors = (
        {"field_name": "employer", "xpath": "//span[@class='company-header-title-name']/text()"},
        {"field_name": "employer_link", "xpath": "//a[@class='g-user-content']/@href"},
        {"field_name": "field", "xpath": "//div[@class='employer-sidebar-block']/p/text()"},
        {"field_name": "com_description", "xpath": "//div[@class='g-user-content']//text()"}

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
        yield from self._get_follow(
            response,
            self._xpath_selectors["employer"],
            self.employer_parse,
        )


    def employer_parse(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        for xpath_strict in self._xpath_employer_selectors:
            loader.add_xpath(**xpath_strict)
        yield loader.load_item()

    def job_parse(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        for xpath_strict in self._xpath_data_selectors:
            loader.add_xpath(**xpath_strict)
        yield loader.load_item()


