import os
from dotenv import load_dotenv
import mysql.connector

# 載入 .env 檔案
load_dotenv()

class DB:
    def __init__(self, host: str = None, database: str = None):
        self.username = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = host or os.getenv("DB_HOST", "140.115.53.151")
        self.database = database or os.getenv("DB_NAME")
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor

# test db connection
# if __name__ == "__main__":
#     db = DB()
#     try:
#         db.connect()
#         print("資料庫連線成功！")
#         db.execute("SELECT * FROM users")
#         rows = db.fetchall()
#         print("users 資料表內容：")
#         for row in rows:
#             print(row)
#     except Exception as e:
#         print("資料庫連線失敗或查詢錯誤：", e)
#     finally:
#         db.close()
