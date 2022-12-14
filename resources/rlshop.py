"""A simple script which will return the current Rocket League shop items in JSON format, according to data scraped from rocket-league.com"""

import requests
from bs4 import BeautifulSoup
import httpx


def get_shop_items():
    scraper = httpx.Client(http2=True)

    URL = "https://rocket-league.com/items/shop"

    page = scraper.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    print(soup.prettify())

    with open('./results.html', 'w') as f:
        f.write(soup.prettify())

    item_containers = soup.find_all("a", {"class": "rlg-item-shop__item"})

    print(item_containers)

    shop_items = []

    for item in item_containers:
        shop_item = {}

        item_name = item.find_all("h1", {"class": "rlg-item-shop__name"})
        item_color = item.find_all("div", {"class": "rlg-item-shop__paint"})
        item_type = item.find_all(
            "div", {"class": "rlg-item-shop__item-category"})
        item_image_url = 'https://rocket-league.com' + \
            item.find_all("img")[0]['src']
        item_price = item.find_all(
            "div", {"class": "rlg-item-shop__item-credits"})

        try:
            shop_item['name'] = item_name[0].text.strip()
        except:
            shop_item['name'] = "Error"

        try:
            shop_item['paint'] = item_color[0].text.strip()
        except:
            shop_item['paint'] = "Unpainted"

        try:
            shop_item['image_url'] = item_image_url.strip()
        except:
            shop_item['image_url'] = "No Image Found"

        try:
            shop_item['type'] = item_type[0].text.strip()
        except:
            shop_item['type'] = "Error"

        try:
            shop_item['price'] = item_price[0].text.strip()
        except:
            shop_item['price'] = "Error"

        shop_items.append(shop_item)

    return (shop_items)


if __name__ == '__main__':
    print(get_shop_items())