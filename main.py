from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from scraper import connect_db
from jsonschema import FormatChecker, validate
import sqlite3
import json

app = FastAPI()

# Generates update query for put request
def generateUpdateQuery(json_data, article_id):
    sql_query_start = "UPDATE article SET"
    sql_query_end = f" WHERE item_id = {article_id}"

    # Adds values to query from put request
    for key, value in json_data.items():
        if isinstance(value, (list,)):
            value_to_str = str(value).replace("'", "")
            sql_query_start += f" {key} = '{value_to_str}',"

        else:
            sql_query_start += f" {key} = '{value}',"

    sql_query_start = sql_query_start[:-1]
    sql_query_start += sql_query_end
    return sql_query_start


@app.get("/")
def home():
    return {"Go to /articles"}


# Get all articles
@app.get("/articles")
def get_all_articles():
    sql_query = """
    SELECT * FROM article
    """

    _, cursor = connect_db()
    cursor.execute(sql_query)
    result = cursor.fetchall()

    return JSONResponse(content=jsonable_encoder({"articles": result}))


# Get articles with same label
@app.get("/articles/")
def get_all_with_label(label: str):
    sql_query = f"SELECT * FROM article WHERE labels LIKE '%{label}%'"
    _, cursor = connect_db()
    cursor.execute(sql_query)
    result = cursor.fetchall()
    if not result:
        return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))
    return JSONResponse(content=jsonable_encoder({"article": result}))


# Get article by date
@app.get("/article/")
def get_article_with_date(date: str):
    sql_query = f"SELECT * FROM article WHERE article_date LIKE '%{date}%'"
    _, cursor = connect_db()
    cursor.execute(sql_query)
    result = cursor.fetchall()
    if not result:
        return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))
    return JSONResponse(content=jsonable_encoder({"article": result}))


# Get single article by id
@app.get("/article/{article_id}")
def get_article(article_id: int):
    sql_query = f"SELECT * FROM article WHERE item_id = {article_id}"
    con, cursor = connect_db()
    cursor.execute(sql_query)
    result = cursor.fetchone()
    if not result:
        return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))
    return JSONResponse(content=jsonable_encoder({"article": result}))


# Delete article by id
@app.delete("/article/{article_id}")
def delete_article(article_id):
    con, cursor = connect_db()
    cursor.execute(f"SELECT * FROM article WHERE item_id = {article_id}")
    result = cursor.fetchone()
    if not result:
        return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))
    sql_query = f"DELETE FROM article WHERE item_id = {article_id}"
    cursor.execute(sql_query)
    con.commit()
    return JSONResponse(content=jsonable_encoder({"message": "article deleted successfully"}))

# Update article info by article_id
@app.put("/article/{article_id}")
async def update_article(article_id, request: Request):
    con, cursor = connect_db()
    cursor.execute(f"SELECT * FROM article WHERE item_id = {article_id}")
    result = cursor.fetchone()
    if not result:
        return JSONResponse(status_code=404, content=jsonable_encoder({"message": "Such article could not be found!"}))
    json_data = await request.json()
    SCHEMA = {
        'properties': {
            'url': {'type': 'string',
                    'pattern': "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"},
            'article_date': {'type': 'string', 'pattern': "^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$"},
            'labels': {'type': 'array', 'pattern': "^["},
            'links': {'type': 'array',
                      'pattern': "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"},
            'body': {'type': 'string'}
        },
        'additionalProperties': False
    }
    try:
        validate(json_data, SCHEMA)
    except Exception as e:
        return JSONResponse(status_code=400, content=jsonable_encoder({"message": "not valid data format"}))

    con, cursor = connect_db()
    cursor.execute(generateUpdateQuery(json_data, article_id))
    con.commit()
    return JSONResponse(content=jsonable_encoder({"message": "Article has been updated"}))