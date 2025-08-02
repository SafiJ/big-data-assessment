# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import io

from scrapy.exporters import CsvItemExporter

fieldnames = ["url", "title", "author", "date"]


class YahooNewsCsvPipeline:
    def open_spider(self, spider):
        self.buffer = io.BytesIO()  # use memory writing because it's on windows
        self.exporter = CsvItemExporter(self.buffer, encoding="utf-8-sig")
        self.exporter.start_exporting()
        spider.logger.info("start writing csv")

    def close_spider(self, spider):
        self.exporter.finish_exporting()

        csv_bytes = self.buffer.getvalue()
        self.buffer.close()

        with open("yahoo_news.csv", "wb") as f:
            f.write(csv_bytes)

        spider.logger.info("CSV data processed from memory and saved.")

    def process_item(self, item, spider):
        """
        will be called every time spider yields an item
        """

        self.exporter.export_item(item)
        return item  # other pipelines can process this item
