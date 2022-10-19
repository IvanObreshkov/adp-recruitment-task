# adp-recruitment-task

This is a repo for the ADP data colection recruitment task v1.2

## Requirements and Installation

Clone the repo

```bash
git clone https://github.com/IvanObreshkov/adp-recruitment-task.git
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install scrapy and fastapi.

```bash
pip install scrapy
```

```bash
pip install "fastapi[all]"
```

## Run crawling script

```bash
cd adp-recruitment-task && scrapy runspider scraper.py
```

## Run API

```bash
cd adp-recruitment-task && uvicorn main:app --reload
```

```bash
cd adp-recruitment-task && scrapy runspider scraper.py
```
