import pymysql
import pymysql.cursors
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'club_user'),
        password=os.getenv('DB_PASSWORD', 'Club_Deportivo#2026'),
        database=os.getenv('DB_NAME', 'club_deportivo'),
        port=int(os.getenv('DB_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
