"""
Project: Parse Coins (on asyncio 3.8.1, Python 3.7)

@author: Stanislav Ermokhin

GitHub: https://github.com/FunnyRabbitIsAHabbit

File: main

Version: 2.0
"""

import asyncio
import pprint

import aiohttp
from lxml.html import etree


class App:
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:45.0) Gecko/20100101 Firefox/45.0'}
    BINANCE_PAGE = "https://www.binance.com/en/markets/newListing"
    COIN_PAGE = "https://coinmarketcap.com/new/"
    BINANCE_TICKERS_XPATH = """//div[@class="css-vlibs4"]"""
    COIN_TICKERS_XPATH = """//*[@class="sc-1eb5slv-0 gGIpIK coin-item-symbol"]"""

    def __init__(self):
        self.data = dict()
        self.p = etree.HTMLParser()
        self.key_1 = 'binance_listed'
        self.key_2 = 'coinmarketcap'

    async def parser(self, html, to_find):
        tree = etree.HTML(html, parser=self.p)
        objects = tree.xpath(to_find)

        return objects

    @staticmethod
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text(encoding="utf-8")

    async def start_session(self, to_find, url):
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            html = await self.fetch(session, url)

            return await self.parser(html, to_find)

    async def pages(self):
        self.data[self.key_1] = await self.start_session(self.BINANCE_TICKERS_XPATH,
                                                         self.BINANCE_PAGE)

        self.data[self.key_2] = await self.start_session(self.COIN_TICKERS_XPATH,
                                                         self.COIN_PAGE)

    @staticmethod
    def convert(arg, source):
        arg = str(arg, encoding="utf-8")
        x = arg[arg.find('>') + 1:arg.find('</')]
        to_find = 'data-bn-type="link" href="/en/trade/'
        ind = x.find(to_find) + len(to_find)

        if "binance" in source:
            return x[ind:x.find('?')] if to_find in x else ''
        else:
            return x

    def main(self):
        asyncio.run(self.pages())

        for key in self.data:
            self.data.update({key: set(map(lambda x: self.convert(etree.tostring(x),
                                                                  source=key),
                                           self.data[key]))})

        return self.data[self.key_1], self.data[self.key_2]


new_app_instance = App()
result = new_app_instance.main()

pprint.pprint(result)
