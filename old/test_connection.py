# test_connection.py
import os
from pathlib import Path
from dotenv import load_dotenv
import pymysql

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

print("接続情報:")
print(f"ホスト: {os.getenv('DB_HOST')}")
print(f"ユーザー: {os.getenv('DB_USER')}")
print(f"データベース: {os.getenv('DB_NAME')}")

try:
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        connect_timeout=10
    )
    print("✓ データベース接続成功!")
    connection.close()
except Exception as e:
    print(f"✗ 接続失敗: {e}")