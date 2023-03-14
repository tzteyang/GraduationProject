import pymysql

ALI_IP = '120.27.209.14'
ALI_USER = 'root'
ALI_PASSWORD = 'SW_MySQL_231'

def conn_ali_mysql(sql, data=None, executemany=False, database='Report', localhost=False):
    # 链接
    conn = pymysql.connect(host='127.0.0.1' if localhost else ALI_IP, user=ALI_USER, password=ALI_PASSWORD, port=22936,
                           database=database,
                           charset='utf8')  # 与数据库的服务端建立连接，database是我们要查询的表所在的数据库

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()

    try:
        # 执行sql语句
        line = cursor.executemany(sql, data) if executemany else cursor.execute(sql, data)
        # 提交到数据库执行
        conn.commit()
        result = cursor.fetchall()

    except Exception as e:
        print(e)
        # 如果发生错误则回滚
        conn.rollback()
        conn.close()
        return None, None

    # 关闭数据库连接
    conn.close()
    return result, line