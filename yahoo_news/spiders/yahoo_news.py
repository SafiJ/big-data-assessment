import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import scrapy
from scrapy.exceptions import CloseSpider

TZ_TAIWAN = "Asia/Taipei"
YAHOO_NEWS_URL = "https://tw.news.yahoo.com"
YAHOO_NEWS_ARCHIVE_URL = "https://tw.news.yahoo.com/archive/"


class YahooNewsSpider(scrapy.Spider):
    name = "yahoo_news"
    start_urls = [YAHOO_NEWS_ARCHIVE_URL]

    api_url = "https://tw.news.yahoo.com/_td-news/api/resource/ListService;api=archive;ncpParams=%7B%22query%22%3A%7B%22count%22%3A{count}%2C%22imageSizes%22%3A%22220x128%22%2C%22documentType%22%3A%22article%2Cvideo%2Cmonetization%22%2C%22start%22%3A{offset}%2C%22tag%22%3Anull%7D%7D?bkt=%5B%22c1-twnews-pc-cg%22%2C%22t1-pc-twnews-article-r3%22%5D&device=desktop&ecma=modern&feature=oathPlayer%2CenableEvPlayer%2CenableGAMAds%2CenableGAMEdgeToEdge%2CvideoDocking&intl=tw&lang=zh-Hant-TW&partner=none&prid=09l1e1tk86746&region=TW&site=news&tz=Asia%2FTaipei&ver=2.3.3077&returnMeta=true"

    def __init__(self, *args, **kwargs):
        hours = float(getattr(self, "hours", 1))
        self.stop_time = datetime.now(ZoneInfo(TZ_TAIWAN)) - timedelta(hours=hours)
        self.log(
            f"Spider will stop at time: {self.stop_time.strftime('%Y-%m-%d %H:%M:%S')} ({hours} hours ago)",
            logging.INFO,
        )
        self.offset = 0
        self.count = 20  # default

    async def start(self):
        yield scrapy.Request(
            self.api_url.format(count=self.count, offset=self.offset),
            callback=self.parse_api,
        )

    def parse_api(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.log(f"cannot parse JSON from {response.url}", logging.ERROR)
            return

        news_list = data.get("data", [])
        if not news_list:
            self.log("API null response, stop crawling", logging.INFO)
            return

        for news in news_list:
            if not news:
                continue

            article_url = YAHOO_NEWS_URL + news["url"]
            title = news["title"].replace(
                "\u3000", " "
            )  # replace full-width (ideographic) space
            author = news["provider_name"]

            # need to extract info from the article page
            yield scrapy.Request(
                article_url,
                callback=self.parse_article,
                meta={"title": title, "author": author},
            )

        # create API request of the older articles
        self.offset += self.count
        yield scrapy.Request(
            self.api_url.format(count=self.count, offset=self.offset),
            callback=self.parse_api,
        )

    def parse_article(self, response):
        datetime_utc_str = response.css("time::attr(datetime)").get()
        local_dt = datetime.fromisoformat(datetime_utc_str).astimezone(
            ZoneInfo(TZ_TAIWAN)
        )
        if local_dt < self.stop_time:
            raise CloseSpider(f"Reached stop time: {self.stop_time}, stop crawling")

        self.log(
            f"scraped news at time: {local_dt.strftime('%Y-%m-%d %H:%M:%S')}",
            logging.INFO,
        )
        yield {
            "url": response.url,
            "title": response.meta["title"],
            "author": response.meta["author"],
            "date": local_dt.date().strftime("%Y-%m-%d"),
        }
