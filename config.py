# config.py
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

# 環境変数から読み込んだデータベース設定
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# データベース接続URLを生成
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"

# Flask-SQLAlchemy用の設定クラス
class Config:
    """データベース設定"""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_NAME
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# config.py - コンフィグファイル
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     """データベース設定"""
#     SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
#         os.getenv('DB_USER'),
#         os.getenv('DB_PASSWORD'),
#         os.getenv('DB_HOST'),
#         os.getenv('DB_PORT'),
#         os.getenv('DB_NAME')
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False