import scrapy, w3lib, re, typing
from datetime import datetime


def clear_html_tags(scraped_list: list) -> list:
    for index, item in enumerate(scraped_list):
        scraped_list[index] = w3lib.html.remove_tags(item.replace('\xa0', ' '))

    return scraped_list


def build_paragraph(scraped_list: list) -> str:
    paragraph = ""
    for item in scraped_list:
        paragraph += " " + item

    return paragraph[1:]


def format_date(scraped_date: list) -> str:
    date = ""
    for item in scraped_date:
        date += item
    date = date.replace(". ", "/")
    formatted_date = datetime.strptime(date, '%d/%m/%Y').date()
    date = formatted_date.strftime('%Y-%m-%d')
    return date


def generate_id(start_urls: list):
    id_of_article = 0
    for articles in start_urls:
        id_of_article = id_of_article + 1
        print(id_of_article)


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    info = {}
    start_urls = ['https://nbs.sk/en/news/nbs-warning-about-axe-capital-group-se/',
                  'https://nbs.sk/en/news/statement-from-the-nbs-bank-boards-17th-meeting-of-2022/']
    article_id: int = 0

    def parse(self, response):
        article_labels: list = clear_html_tags(
            response.xpath('//ul[contains(@class, "menu menu--labels")]//li//div').getall())
        article_paragraphs: list = clear_html_tags(
            response.xpath('//div[contains(@class, "nbs-post__block")]//p').getall())
        article_date: list = clear_html_tags(response.xpath('//div[contains(@class, "nbs-post__date")]').getall())
        date: str = format_date(article_date)
        paragraphs: str = build_paragraph(article_paragraphs)
        article_links: list = re.findall(
            "(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})",
            paragraphs)
        self.article_id = self.article_id + 1;

        with open('file.txt', 'a') as file:
            file.write("\nitem_id: {}".format(self.article_id))
            file.write("\nurl: {}".format(self.start_urls[self.article_id-1]))
            file.write("\ndate: {}".format(date))
            file.write("\nlabels: {}".format(article_labels))
            file.write("\nlinks: {}".format(str(article_links)))
            file.write("\nbody: {}".format(paragraphs))
