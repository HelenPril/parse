import json
import time
from pathlib import Path
import requests
from urllib.parse import urlparse


class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    __parse_time = 0


    def __init__(self, start_url, save_path, delay=0.2):
        self.start_url = start_url
        self.save_path = save_path
        self.delay = delay

    def run(self):
        for itog, category in self._category(self.start_url):
            file_path = self.save_path.joinpath(f"{category['parent_group_code']}.json")
            self.save(itog, file_path)

    def _get_response(self, url):
        next_time = self.__parse_time + self.delay
        url = url.replace(urlparse(url).netloc, urlparse(self.start_url).netloc)
        while True:
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response
            time.sleep(self.delay)

    def _category(self, url):
        response = self._get_response(url)
        len_data = len(response.json())
        for i in range(len_data):
            data = response.json()
            for category in data:
                code = str(category['parent_group_code'])
                name = str(category['parent_group_name'])
                url_new = url + code + '/'
                response_prod = self._get_response(url_new)
                data_prod = response_prod.json()
                spisok_prod = []
                for i in data_prod:
                    a = i['group_name']
                    b = i['group_code']
                    c = {b: a}
                    spisok_prod.append(c)
                itog = {
                    "name": name,
                    "code": code,
                    "products": spisok_prod
                }
                yield itog, category


    def save(self, data: dict, save_path):
        save_path.write_text(json.dumps(data, ensure_ascii=False))


def get_save_dir(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


if __name__ == '__main__':
    url = "https://5ka.ru/api/v2/categories/"
    categories_dir = get_save_dir("categories_proba")
    parser = Parse5ka(url, categories_dir)
    parser.run()
