from pathlib import Path

import requests


"""
HTTPs
request/response
headers:
body:

- GET
- POST
- PUT
- PATCH
- DELETE
- INFO
"""


temp_file = Path(__file__).parent.joinpath("temp.html")

url = "https://5ka.ru/special_offers/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"
}
response = requests.get(url, headers=headers)
temp_file.write_bytes(response.content)

