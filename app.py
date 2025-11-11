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


# ==========================
# ログイン処理
# ==========================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            employee_id = request.form.get('employee_id')
            user_password = request.form.get('password')

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


# ==========================
# ホーム画面
# ==========================
@app.route('/home', methods=['GET'])
def home():
    user_name = session.get('user_name')
    if user_name:
        return render_template('index.html', employee_id=session.get('user_id'), user_name=user_name)
    else:
        return redirect(url_for('login'))


# ==========================
# ページルート
# ==========================
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


# ==========================
# 画像アップロードAPI
# ==========================
@app.route('/api/inspection/<int:inspection_id>/upload_photo', methods=['POST'])
def upload_photo(inspection_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        photo_data = data.get('photo_data')
        filename = data.get('filename', f'inspection_{inspection_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')

        if not photo_data:
            return jsonify({'error': 'No photo data provided'}), 400

        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]

        image_binary = base64.b64decode(photo_data)

        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(image_binary)

        sys.stderr.write(f"画像保存成功: {filepath}\n")
        sys.stderr.write(f"ファイルサイズ: {len(image_binary)} bytes\n")
        sys.stderr.flush()

        # ==============================
        # DB更新処理
        # ==============================
        inspection = Inspection.query.get(inspection_id)
        if inspection:
            inspection.photo_filename = filename
            inspection.image_url = f'/static/uploads/{filename}'
            inspection.photo_uploaded_at = datetime.now()
            db.session.commit()
            sys.stderr.write(f"✅ DB更新成功: inspection_id={inspection_id}, filename={filename}\n")
            sys.stderr.flush()
        else:
            sys.stderr.write(f"⚠️ Inspection ID {inspection_id} がDBに存在しません\n")
            sys.stderr.flush()
            return jsonify({'error': 'Inspection not found'}), 404

        return jsonify({
            'success': True,
            'message': 'Photo uploaded and saved to database',
            'inspection_id': inspection_id,
            'filename': filename,
            'filepath': f'/static/uploads/{filename}'
        }), 200

    except Exception as e:
        sys.stderr.write(f"❌ エラー発生: {str(e)}\n")
        sys.stderr.flush()
        return jsonify({'error': str(e), 'message': 'Failed to upload photo'}), 500

@app.route('/api/inspection/<int:inspection_id>', methods=['GET'])
def get_inspection(inspection_id):
    """指定された inspection_id の点検結果を取得して返すAPI"""
    try:
        inspection = Inspection.query.get(inspection_id)
        if not inspection:
            sys.stderr.write(f"⚠️ Inspection ID {inspection_id} が見つかりませんでした\n")
            sys.stderr.flush()
            return jsonify({'error': 'Inspection not found'}), 404

        sys.stderr.write(f"✅ Inspection ID {inspection_id} のデータ取得成功\n")
        sys.stderr.write(f" - result: {inspection.result}\n")
        sys.stderr.write(f" - overall_result: {inspection.overall_result}\n")
        sys.stderr.write(f" - inspection_date: {inspection.inspection_date}\n")
        sys.stderr.write(f" - photo_filename: {inspection.photo_filename}\n")
        sys.stderr.write(f" - image_url: {inspection.image_url}\n")
        sys.stderr.flush()

        return jsonify({
            'inspection_id': inspection.inspection_id,
            'chain_grade': inspection.result or inspection.overall_result or None,
            'inspection_date': inspection.inspection_date.strftime("%Y-%m-%d") if inspection.inspection_date else None,
            'photo_filename': inspection.photo_filename,
            'image_url': inspection.image_url
        }), 200

    except Exception as e:
        sys.stderr.write(f"❌ /api/inspection/{inspection_id} API エラー: {str(e)}\n")
        sys.stderr.flush()
        return jsonify({'error': str(e)}), 500
# ==========================
# DB初期化チェック
# ==========================
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
