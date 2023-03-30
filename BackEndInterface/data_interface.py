from flask import Flask, jsonify
from utils.db_conn import local_db
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 借助扩展flask_cors 允许所有跨域请求

@app.route('/')
def test():
    db = local_db(database='report', datasource='local')
    
    sql = "select * from inventors_crawl limit 1"
    result = db.query_one(sql)
    response = jsonify(result)

    db.db_close()
    return response

if __name__ == '__main__':
    app.run()