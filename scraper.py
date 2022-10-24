import scrapy, w3lib, re, typing, json
from datetime import datetime
import sqlite3


# Remove html tags
def clear_html_tags(scraped_list: list) -> list:
    for index, item in enumerate(scraped_list):
        scraped_list[index] = w3lib.html.remove_tags(item.replace('\xa0', ' '))

    return scraped_list


# Construct paragraphs without html tags
def build_paragraph(scraped_list: list) -> str:
    paragraph = ""
    for item in scraped_list:
        paragraph += " " + item

    return paragraph[1:]


# Get date from article and return it in a proper format
def format_date(scraped_date: list) -> str:
    date = ""
    for item in scraped_date:
        date += item
    date = date.replace(". ", "/")
    formatted_date = datetime.strptime(date, '%d/%m/%Y').date()
    date = formatted_date.strftime('%Y-%m-%d')
    return date


# Connect to SQLite Database
def connect_db():
    con = sqlite3.connect("articles.db")
    con.row_factory = sqlite3.Row

    cursor = con.cursor()
    create_table(con, cursor)
    return con, cursor


# Create table to store articles
def create_table(con, cursor):
    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS article (
                                            item_id integer PRIMARY KEY AUTOINCREMENT,
                                            url text NULL,
                                            article_date text NOT NULL,
                                            labels text NOT NULL,
                                            links text integer NOT NULL,
                                            body TEXT NOT NULL
                                        );"""

    try:
        cursor.execute(sql_create_tasks_table)
        con.commit()
    except Exception as e:
        print(e)


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    info = {}
    start_urls = ['https://nbs.sk/en/news/nbs-warning-about-axe-capital-group-se/',
                  'https://nbs.sk/en/news/statement-from-the-nbs-bank-boards-17th-meeting-of-2022/',
                  'https://nbs.sk/en/news/statement-from-the-nbs-bank-boards-18th-meeting-of-2022%ef%bf%bc/',
                  'https://nbs.sk/en/news/statement-from-the-nbs-bank-boards-16th-meeting-of-2022/',
                  'https://nbs.sk/en/news/nbs-warning-about-feb-bank/',
                  'https://nbs.sk/en/news/statement-from-the-nbs-bank-boards-12th-meeting-of-2022/',
                  'https://nbs.sk/en/news/statement-from-the-nbs-bank-boards-9th-meeting-of-2022/',
                  'https://nbs.sk/en/news/statement-from-the-1st-meeting-of-the-bank-board-of-the-nbs/',
                  'https://nbs.sk/en/news/nbs-warning-about-salus-populi/',
                  'https://nbs.sk/en/news/nbs-warning-about-proof-of-no-debt-documents-provided-through-the-website-of-the-central-register-of-debtors-of-the-slovak-republic-cerd/',
                  'https://nbs.sk/en/news/novis-insurance-company/',
                  'https://nbs.sk/en/news/nbs-warning-about-the-activities-of-ci-investment-group-s-r-o-operator-of-the-platform-www-investiciaslovensko-sk/',
                  'https://nbs.sk/en/news/nbs-warning-about-the-activities-of-world-agency-s-r-o-operator-of-the-website-www-worldagency-sk/',
                  'https://nbs.sk/en/news/nbs-warns-about-misleading-advertisements-for-alternative-bank-accounts/',
                  'https://nbs.sk/en/news/coronavirus-postponement-of-start-of-sales-of-e10-silver-collector-coin-andrej-sladkovic/',
                  'https://nbs.sk/en/news/nbs-announces-temporary-closure-of-public-counters-and-filing-office/',
                  'https://nbs.sk/en/news/nbs-launches-research-archive-portal/',
                  'https://nbs.sk/en/news/notice-of-the-commencement-of-winding-up-proceedings-against-lamp-insurance-company-limited/',
                  'https://nbs.sk/en/news/nbs-warning-what-is-a-pyramid-scheme-airplane-game-or-ponzi-scheme/',
                  'https://nbs.sk/en/news/the-european-systemic-risk-board-issues-a-warning-to-slovakia-on-vulnerabilities-in-the-residential-real-estate-sector/'
                  ]

    con, cursor = connect_db()

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

        schema = {
            "url": response.request.url,
            "article_date": date,
            "labels": str(article_labels),
            "links": str(article_links),
            "body": paragraphs
        }

        try:
            # Checks if a new article's body matches the body of an existing article in the db

            sql_check_duplicates = f" SELECT * FROM article WHERE body = '{paragraphs}'"
            self.cursor.execute(sql_check_duplicates)
            result = self.cursor.fetchone()
            if not result:
                self.cursor.execute(
                    "INSERT INTO article (url, article_date, labels, links, body) VALUES (:url, :article_date, :labels, :links, :body)",
                    schema)
                self.con.commit()
            else:
                print("Duplicate are not allowed")
        except Exception as e:
            print(e)

