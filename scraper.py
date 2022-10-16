import scrapy, w3lib, re


def clear_html_tags(scraped_list: list) -> list:
    for index, item in enumerate(scraped_list):
        scraped_list[index] = w3lib.html.remove_tags(item.replace('\xa0', ' '))

    return scraped_list


def build_paragraph(scraped_list: list) -> str:
    paragraph = ""
    for item in scraped_list:
        paragraph += " " + item

    return paragraph[1:]


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    info = {}
    start_urls = ['https://nbs.sk/en/news/nbs-warning-about-axe-capital-group-se/',
                  'https://nbs.sk/en/news/statement-from-the-nbs-bank-boards-17th-meeting-of-2022/']

    def parse(self, response):
        ## think of how to optimize this
        article_labels: list = clear_html_tags(
            response.xpath('//ul[contains(@class, "menu menu--labels")]//li//div').getall())
        article_paragraphs: list = clear_html_tags(
            response.xpath('//div[contains(@class, "nbs-post__block")]//p').getall())

        paragraphs: str = build_paragraph(article_paragraphs)
        article_links: list = re.findall("(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", paragraphs)

        with open('file.txt', 'a') as file:
            file.write("\nlabels: {}".format(article_labels))
            file.write("\nparagraphs: {}".format(paragraphs))
            file.write("\nlinks: {}".format(str(article_links)))
