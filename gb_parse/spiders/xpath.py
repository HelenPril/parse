HH_PAGE_XPATH = {
    "pagination": "//div[@data-qa='pager-block']//a[@class='bloko-button']/@href",
    "job": "//div[contains(@class, 'vacancy-serp-item')]//a[@class='bloko-link']/@href",
}

HH_VACANCY_XPATH = {
    "title": "//h1[@data-qa='vacancy-title']/text()",
    "salary": "//p[@class='vacancy-salary']//text()",
    "skills": "//div[contains(@class,'bloko-tag')]//text()",
    "description": "//div[@class='vacancy-description']//text()",
    "author_name": "//span[@class='bloko-section-header-2 bloko-section-header-2_lite']//text()",
    "author_link": "//a[@class='vacancy-company-name']/@href",
}