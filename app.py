from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from models import db, User, Park, Equipment, Inspection, Report
from config import DATABASE_URL
import os


app = Flask(__name__)

# セッションの設定
app.config['SECRET_KEY'] = os.urandom(24)  # ランダムな秘密鍵を生成
app.config['SESSION_TYPE'] = 'filesystem'  # セッションの保存方法をファイルシステムに設定

# 設定を読み込む
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Flask-Migrateの初期化（マイグレーション機能）
migrate = Migrate(app, db)
error = False

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            employee_id = request.form.get('employee_id')
            user_password = request.form.get('password')
            
            # ユーザー情報の検索
            user = User.query.filter_by(employee_id=employee_id).first()
            
            if user and user_password == user.password:
                # ログイン成功
                session['user_id'] = user.employee_id
                session['user_password'] = user.password
                session['user_name'] = user.name
                return redirect(url_for('index'))
            else:
                # ログイン失敗
                return render_template('Login.html', error="ユーザー名またはパスワードが正しくありません")
                
        except Exception as e:
            # エラー発生時
            return render_template('Login.html', error="システムエラーが発生しました")
            
    # GET時はログインフォームを表示
    return render_template('Login.html')

@app.route('/home', methods=['GET'])
def index():
    # セッションからユーザー情報を取得
    user_name = session.get('user_name')
    if user_name:
        return render_template('index.html', employee_id=session.get('user_id'), user_name=user_name)
    else:
        return redirect(url_for('home'))

@app.route('/daily_report', methods=['GET'])
def daily_report():
    return redirect(url_for('daily_report'))


@app.route('/inspection_check', methods=['GET'])
def inspection_check():
    return redirect(url_for('inspection_check'))


# テーブルを一度だけ作成するためのフラグ
tables_created = os.path.exists('db_initialized.flag')

if not tables_created:
    with app.app_context():
        db.create_all()
        print("テーブルが作成されました")
        # データベースが作成されたことを示すフラグを作成
        with open('db_initialized.flag', 'w') as f:
            f.write('created')
    print("データベースが初期化されました")
else:
    print("データベースはすでに初期化されています")

if __name__ == '__main__':
    app.run(debug=True)