import json
import time
import typing

import requests #запрос
from urllib.parse import urljoin #склеивание url, когда у нас в начале получается относительная ссылка без домена /post?page=2
import bs4
import pymongo

import datetime as dt


class GbBlogParse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) "
        "Gecko/20100101 Firefox/88.0"
    }
    __parse_time = 0

    def __init__(self, stat_url, collection, delay=1.0):
        self.start_url = stat_url
        self.collection = collection
        self.delay = delay
        self.done_urls = set() #чтобы следить за тем, где мы были; set, так как он меньше списка, быстрота поиска (хэш-таблица) и уникальность
        self.tasks = [] #список, где будут храниться наши задачи
        self.task_creator(self.start_url, callback=self.parse_feed) #здесь будут задачи

    def _get_response(self, url): #ответ
        #здесь у нас не будет строчки с переделкой url, так как на этом сайте они норм, а не изменяются, как в пятерочке
        next_time = self.__parse_time + self.delay
        while True:
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response
            time.sleep(self.delay)

    def _get_soup(self, url):
        response = self._get_response(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable: #Callable-объекты - это обекты, которые можно вызывать а(), те ф-ции
        #будет создавать задачи (поэтому возвращаем тоже ф-ции, так как это и есть задача)
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def task_creator(self, *urls, callback):
        urls_set = set(urls) - self.done_urls #убирает все дубли
        for url in urls_set:
            self.tasks.append(self.get_task(url, callback))
            self.done_urls.add(url)

    def parse_feed(self, url, soup): #лента (все ссылки на пагинацию и посты)
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        pag_links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in ul_pagination.find_all("a")
            if itm.attrs.get("href")
        )
        self.task_creator(*pag_links, callback=self.parse_feed)
        post_links = set(
            urljoin(url, itm.attrs.get("href"))
            for itm in soup.find_all("a", attrs={"class": "post-item__title"})
            if itm.attrs.get("href")
        )
        self.task_creator(*post_links, callback=self.parse_post)

    def parse_post(self, url, soup):
        image = soup.find("div", attrs={"class": "blogpost-content content_text content js-mediator-article"})
        link = soup.find("div", attrs={"class": "col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v"})
        author_link = link.find("a")
        final_link = urljoin(url, author_link.attrs.get("href"))
        datetime = soup.find("time", attrs={"class": "text-md text-muted m-r-md"})
        datetime_str = datetime.attrs.get("datetime")
        datetime_done = dt.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S%z")

        data = {
            "url": url,
            "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
            "image": image.attrs.get("src"),
            "datetime": datetime_done,
            "author": soup.find("div", attrs={"class": "text-lg text-dark"}).text,
            "author_link": final_link,
            "tags_data": [
                {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comments(soup.find("comments").attrs.get("commentable-id"))
        }
        return data

    def _get_comments(self, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = self._get_response(urljoin(self.start_url, api_path))
        data = response.json()
        return data

    def run(self):
        while True:
            try:
                task = self.tasks.pop(0)
            except IndexError: #чтобы очищать очередь
                break
            result = task()
            if isinstance(result, dict): #проверка, что объект является словарем
                self.save(result)

    def save(self, data):
        self.collection.insert_one(data)
        print(1)


if __name__ == "__main__":
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    db = mongo_client["les2"] #здесь нужно указать название файла, который будем приконекчивать к Mongo
    collection = db["gb_blog_parse"]
    parser = GbBlogParse("https://gb.ru/posts", collection, delay=0.1) #даем сокращенное имя нашему классу и вызываем его через переменные)
                        #то, что сейчас в скобочках передается к конструктор init
    parser.run()