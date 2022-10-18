from fastapi import FastAPI
from scraper import connect_db

#initailize FastApi instance
app = FastAPI()


#define endpoint
@app.get("/")
def home():
    return {"Go to /articles"}

@app.get("/articles")
def list_all_articles():
    sql_action = """
    SELECT * FROM acticle
    """
    con, cursor = connect_db()
    data = cursor.execute(sql_action)
    con.commit()
    return type(data)
