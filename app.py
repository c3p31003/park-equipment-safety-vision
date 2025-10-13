from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import check_password_hash
from models import Users, db

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # セッション用の秘密鍵（本番環境では環境変数から読み込む）

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
    





if __name__ == '__main__':
    app.run(debug=True)