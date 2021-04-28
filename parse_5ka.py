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


    def __init__(self, start_url, save_path, delay=1):
        self.start_url = start_url
        self.save_path = save_path
        self.delay = delay

    def run(self):
        for product in self._parse(self.start_url):
            file_path = self.save_path.joinpath(f"{product['id']}.json")
            self.save(product, file_path)

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

    def _parse(self, url):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data.get('next')
            for product in data.get("results", []):
                yield product

    def save(self, data: dict, save_path):
        save_path.write_text(json.dumps(data, ensure_ascii=False))


def get_save_dir(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


if __name__ == '__main__':
    url = "https://5ka.ru/api/v2/special_offers/"
    products_dir = get_save_dir("products")
    parser = Parse5ka(url, products_dir)
    parser.run()

