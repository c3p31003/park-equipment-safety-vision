# test.py - config.pyのDATABASE_URLを使用した接続テスト
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
import os

# config.pyからDATABASE_URLをインポート
from config import DATABASE_URL

# 環境変数のロード
load_dotenv()

# Flaskアプリケーションの初期化
app = Flask(__name__)

# SQLAlchemyの設定
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy初期化
db = SQLAlchemy(app)

def test_connection():
    """データベース接続テスト"""
    # 接続情報の表示（パスワードは伏字）
    connection_url = DATABASE_URL.replace(
        os.getenv('DB_PASSWORD'),
        '***'
    )
    print(f"接続情報: {connection_url}")
    
    try:
        # アプリケーションコンテキストで実行
        with app.app_context():
            # SQLを実行して接続確認
            db.session.execute(text('SELECT 1'))
            print("データベース接続成功")
            return True
    except Exception as e:
        print(f"データベース接続失敗: {e}")
        return False

if __name__ == "__main__":
    test_connection()