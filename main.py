from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from scraper import connect_db
from jsonschema import FormatChecker, validate
import sqlite3
import json

app = FastAPI()


@app.get("/")
def home():
    return {"Go to /articles"}


# Get all articles
@app.get("/articles")
def get_all_articles():
    sql_query = """
    SELECT * FROM article
    """

    _, cursor = connect_db(row=True)
    cursor.execute(sql_query)
    result = cursor.fetchall()

    return JSONResponse(content=jsonable_encoder({"articles": result}))


# Get articles with same label
@app.get("/articles/")
def get_all_with_label(label: str):
    sql_query = f"SELECT * FROM article WHERE labels LIKE '%{label}%'"
    _, cursor = connect_db(row=True)
    cursor.execute(sql_query)
    result = cursor.fetchall()
    if not result:
        return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))
    return JSONResponse(content=jsonable_encoder({"article": result}))


# Get article by date
@app.get("/article/")
def get_article_with_date(date: str):
    sql_query = f"SELECT * FROM article WHERE article_date LIKE '%{date}%'"
    _, cursor = connect_db(row=True)
    cursor.execute(sql_query)
    result = cursor.fetchall()
    if not result:
        return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))
    return JSONResponse(content=jsonable_encoder({"article": result}))


# Get single article by id
@app.get("/article/{article_id}")
def get_article(article_id: int):
    sql_query = f"SELECT * FROM article WHERE item_id = {article_id}"
    con, cursor = connect_db(row=True)
    cursor.execute(sql_query)
    result = cursor.fetchone()
    if not result:
        return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))
    return JSONResponse(content=jsonable_encoder({"article": result}))


# Delete article by id
@app.delete("/article/{article_id}")
def delete_article(article_id):
    sql_query = f"DELETE FROM article WHERE item_id = {article_id}"
    con, cursor = connect_db(row=True)
    cursor.execute(sql_query)
    con.commit()
    if (int(article_id) >= 1 and int(article_id) <= 20):
        return JSONResponse(content=jsonable_encoder({"message": "article deleted successfully"}))
    return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))


@app.put("/article/{article_id}")
async def update_article(article_id, request: Request):
    json_data = await request.json()
    SCHEMA = {
        'article': {
            'item_id': {'type': 'string'},
            'url': {'type': 'string',
                    'pattern': "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"},
            'article_date': {'type': 'string', 'pattern': "^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$"},
            'labels': {'type': 'string', 'pattern': "^["},
            'links': {'type': 'string',
                      'pattern': "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"},
            'body': {'type': 'string'}
        }
    }

    try:
        val_response = validate(json_data, SCHEMA)
        print(val_response)
    except Exception as e:
        return JSONResponse(status_code=400, content=jsonable_encoder({"message": "not valid data format"}))

    # TO-DO
    # Do a query to update a whole article
    return JSONResponse(content=jsonable_encoder({"data": json_data}))
