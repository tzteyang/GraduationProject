import pymysql

class local_db:

    def __init__(self, database):
        try:
            self.conn = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='yang8302',
                database=database,
                cursorclass=pymysql.cursors.DictCursor,
                charset='utf8',
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)
            print('connect database wrong!!!')

    def db_edit(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            print('database edit wrong!!!')

    def query_one(self, sql):
        # 查询为空的返回值
        result = None
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
        except Exception as e:
            print(e)
            print('database query wrong!!!')

        return result

    def query_all(self, sql):
        results = ()
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
        except Exception as e:
            print(e)
            print('database query wrong!!!')

        return results

    def db_close(self):
        self.cursor.close()
        self.conn.close()
