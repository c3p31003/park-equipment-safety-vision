from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from old.models import db
from old.config import DATABASE_URL, SECRET_KEY

app = Flask(__name__)

# 設定を読み込む
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

# Flask-Migrateの初期化（マイグレーション機能）
migrate = Migrate(app, db)

@app.route('/')
def home():
    # ログイン済みならindex.htmlへ、未ログインならログインページへ
    if 'employee_id' in session:
        return render_template('index.html')
    return render_template('Login.html')

@app.route('/login', methods=['POST'])
def login():
    employee_id = request.form.get('employee_id')
    password = request.form.get('password')
    


db.init_app(app)

with app.app_context():
    db.create_all() # テーブルを作成


if __name__ == '__main__':
    app.run(debug=True)