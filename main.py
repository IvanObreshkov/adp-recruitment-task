from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from scraper import connect_db
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
    # verify json data
    # if data is ok
    # do sql query update article if article_id exists and return message on success
    # if not return appropriate res code and message

    return JSONResponse(content=jsonable_encoder({"data": json_data}))