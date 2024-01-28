import scrapy
import json
from scrapy.crawler import CrawlerProcess

import connect_mongo
from models import Author, Quotes 

url = 'quotes.toscrape.com'
filename_quotes = "quotes.json"
filename_authors = "authors.json"


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = [url]
    start_urls = [f'http://{url}/']
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": filename_quotes}

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            yield {
                "tags": quote.xpath("div[@class='tags']/a/text()").getall(),
                "author": quote.xpath("span/small[@class='author']/text()").get(),
                "quote": quote.xpath("span[@class='text']/text()").get()
            }

        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            yield scrapy.Request(url=self.start_urls[0] + next_page)

class AuthorsSpider(scrapy.Spider):
    name = 'authors'
    allowed_domains = [url]
    start_urls = [f'http://{url}/']
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": filename_authors}

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='author-details']"):
            yield {
                "fullname": quote.xpath("h3[@class='author-title']/text()").get(),
                "born_date": quote.xpath("p/span[@class='author-born-date']/text()").get(),
                "born_location": quote.xpath("p/span[@class='author-born-location']/text()").get(),
                "description": quote.xpath("div[@class='author-description']/text()").get().replace('\n', ' ').strip()
            }
      
        authors_on_page = response.xpath("/html//div[@class='quote']/span/a/@href").getall()
        for next_author in authors_on_page:
            yield scrapy.Request(url=self.start_urls[0] + next_author)

        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page is not None:
            yield scrapy.Request(url=self.start_urls[0] + next_page)

def run_spiders():
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.crawl(AuthorsSpider)
    process.start()

def save_to_mongo():

    def read_json(file):
        with open(file, "r", encoding='utf-8') as f:
            return json.load(f)

    Author.drop_collection()
    Quotes.drop_collection()

    authors = read_json(filename_authors)
    quotes = read_json(filename_quotes)

    for author in authors:
        Author(**author).save()

    for quote in quotes:
        author_name = Author.objects(fullname=quote['author']).first()
        quote['author'] = author_name
        Quotes(**quote).save()

if __name__ == "__main__":
    run_spiders()
    save_to_mongo()
