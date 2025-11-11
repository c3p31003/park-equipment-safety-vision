from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from models import db, User, Park, Equipment, Inspection, Report
from config import DATABASE_URL
import os
import sys  
import base64
from datetime import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-fixed-secret-key-change-this-in-production'
app.config['SESSION_TYPE'] = 'filesystem'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            employee_id = request.form.get('employee_id')
            user_password = request.form.get('password')

            # ✅ print の代わりに sys.stderr を使用（確実に表示される）
            sys.stderr.write(f"\n【デバッグ】フォーム入力 - employee_id: {employee_id}, password: {user_password}\n")
            sys.stderr.flush()

            user = None
            try:
                sys.stderr.write(f"【デバッグ】DB検索開始: employee_id={int(employee_id)}\n")
                sys.stderr.flush()
                
                user = User.query.filter_by(employee_id=int(employee_id)).first()
                
                sys.stderr.write(f"【デバッグ】DB検索結果: user={user}\n")
                if user:
                    sys.stderr.write(f"【デバッグ】 - DB employee_id: {user.employee_id}\n")
                    sys.stderr.write(f"【デバッグ】 - DB password: {user.password}\n")
                sys.stderr.flush()
                
            except Exception as e:
                sys.stderr.write(f"【デバッグ】クエリエラー: {e}\n")
                sys.stderr.flush()

            # ✅ パスワード比較の詳細ログ
            sys.stderr.write(f"【デバッグ】認証判定:\n")
            sys.stderr.write(f"  user is not None: {user is not None}\n")
            if user:
                sys.stderr.write(f"  パスワード一致: {user_password} == {user.password} → {user_password == user.password}\n")
            sys.stderr.flush()

            if user and user_password == user.password:
                session['user_id'] = user.employee_id
                session['user_password'] = user.password
                session['user_name'] = user.name
                sys.stderr.write(f"【デバッグ】認証成功！ /home にリダイレクト\n")
                sys.stderr.flush()
                return redirect(url_for('home'))
            else:
                sys.stderr.write(f"【デバッグ】認証失敗\n")
                sys.stderr.flush()
                return render_template('Login.html', error="ユーザー名またはパスワードが正しくありません")
        except Exception as e:
            sys.stderr.write(f"【デバッグ】エラー発生: {e}\n")
            sys.stderr.flush()
            return render_template('Login.html', error="エラーが発生しました。再度お試しください。")
    
    return render_template('Login.html')


@app.route('/home', methods=['GET'])
def home():
    user_name = session.get('user_name')
    if user_name:
        return render_template('index.html', employee_id=session.get('user_id'), user_name=user_name)
    else:
        return redirect(url_for('login'))
    

@app.route('/CheckSheet')   
def CheckSheet(): 
    return render_template('CheckSheet.html')

@app.route('/daily_report')
def daily_report(): 
    return render_template('daily_report.html')

@app.route('/inspection_results')   
def inspection_results(): 
    return render_template('inspection_results.html')

@app.route('/AllDocuments')   
def AllDocuments(): 
    return render_template('AllDocuments.html')

@app.route('/PhotoViewing')   
def PhotoViewing(): 
    return render_template('PhotoViewing.html')

@app.route('/TakePhoto')   
def TakePhoto(): 
    return render_template('TakePhoto.html')

@app.route('/api/inspection/<int:inspection_id>/upload_photo', methods=['POST'])
def upload_photo(inspection_id):
    """
    【機能】
    - フロントエンドから送信された画像データ(Base64)を受信
    - デコードしてファイルとして保存
    - 成功/失敗のレスポンスを返す
    """
    try:
        # ====================================================
        # 【ステップ1】JSONデータを受信
        # ====================================================
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        photo_data = data.get('photo_data')
        filename = data.get('filename', f'inspection_{inspection_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        if not photo_data:
            return jsonify({'error': 'No photo data provided'}), 400
        
        # ====================================================
        # 【ステップ2】Base64データからヘッダーを除去
        # ====================================================
        # フロントエンドから送られるデータ形式:
        # "data:image/png;base64,iVBORw0KGgoAAAANS..."
        #                      ↑ この部分だけが必要
        
        if ',' in photo_data:
            # "data:image/png;base64," の部分を削除
            photo_data = photo_data.split(',')[1]
        
        # ====================================================
        # 【ステップ3】Base64 → バイナリデータに変換
        # ====================================================
        try:
            image_binary = base64.b64decode(photo_data)
        except Exception as e:
            return jsonify({'error': f'Invalid base64 data: {str(e)}'}), 400
        
        # ====================================================
        # 【ステップ4】保存先ディレクトリの準備
        # ====================================================
        # static/uploads/ ディレクトリを作成（存在しない場合）
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            sys.stderr.write(f"📁 ディレクトリ作成: {upload_dir}\n")
            sys.stderr.flush()
        
        # ====================================================
        # 【ステップ5】ファイルとして保存
        # ====================================================
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_binary)
        
        sys.stderr.write(f"画像保存成功: {filepath}\n")
        sys.stderr.write(f"ファイルサイズ: {len(image_binary)} bytes\n")
        sys.stderr.flush()
        
        # ====================================================
        # 【ステップ6】成功レスポンスを返す
        # ====================================================
        return jsonify({
            'success': True,
            'message': 'Photo uploaded successfully',
            'inspection_id': inspection_id,
            'filename': filename,
            'filepath': f'/static/uploads/{filename}'
        }), 200
        
    except Exception as e:
        # ====================================================
        # 【エラーハンドリング】
        # ====================================================
        sys.stderr.write(f"❌ エラー発生: {str(e)}\n")
        sys.stderr.flush()
        
        return jsonify({
            'error': str(e),
            'message': 'Failed to upload photo'
        }), 500


tables_created = os.path.exists('db_initialized.flag')

if not tables_created:
    with app.app_context():
        db.create_all()
        print("テーブルが作成されました")
        with open('db_initialized.flag', 'w') as f:
            f.write('created')
    print("データベースが初期化されました")


if __name__ == '__main__':
    app.run(debug=True)