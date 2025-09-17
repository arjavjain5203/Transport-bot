import pymysql
from core.config import settings

def get_connection():
    conn = pymysql.connect(
        host=settings.DB_HOST,
        port=int(settings.DB_PORT),
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def run_query(query, params=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)  # run plain query if no params
            result = cursor.fetchall()
        connection.commit()
    finally:
        connection.close()
    return result
