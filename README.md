# big-data assessment

Requirements
1. 以Scrapy框架進行Yahoo新聞的資料收錄，根據完成時間收錄近一小時的新聞文章。
e.g. 5/28 16:00完成開發，請將5/28 15:00~16:00匯出成csv，欄位需包含連結、標題、作者、日期。
2. 請收錄以下臉書社團近三個月的貼文及留言，並以restful api的方式提供給我們進行呼叫。
回傳的欄位包含 : 類型(主文/留言)、內容、時間、發文者/留言者
https://www.facebook.com/groups/443709852472133?locale=zh_TW

 - [x] Yahoo News Scraper
 - [ ] RESTful API endpoint


## Yahoo News Scraper
1. install dependencies
```bash
pip install -r requirements.txt
```
2. quick run (you can decide how many hours of news you want to scrape)
```bash
scrapy crawl yahoo_news -a hours=1
```
