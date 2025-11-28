from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from models import db, User, Park, Equipment, Inspection, Report
from config import DATABASE_URL
import os
import sys
import base64
from datetime import datetime
from keras.models import load_model
from keras.preprocessing import image
from PIL import Image
import io
import numpy as np


app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-fixed-secret-key-change-this-in-production'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

#モデル読み込み
MODEL_PATH = './chain_cnn_aug_best.keras'
IMG_SIZE = 64
CLASSES = ['nomal', 'rust']

try:
    inference_model = load_model(MODEL_PATH)
    print(f"モデルが正常に読み込まれました: {MODEL_PATH}")
except Exception as e:
    sys.stderr.write(f"モデルの読み込みエラー: {e}\n")
    sys.stderr.flush()
    inference_model = None

def predict_rust(image_binary):
    if inference_model is None:
        return None, None
    try:
        #bainaryデータをPIL Imageに変換
        img = Image.open(io.BytesIO(image_binary))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((IMG_SIZE, IMG_SIZE))
        img_array = np.array(img, dtype='float32') / 255.0
        img_batch = np.expand_dims(img_array, axis=0)
        # 予測実行
        predictions = inference_model.predict(img_batch, verbose=0)
        # 予測結果を取得
        confidence = float(np.max(predictions[0]))
        predicted_class_index = int(np.argmax(predictions[0]))
        predicted_class = CLASSES[predicted_class_index]
        
        sys.stderr.write(f"予測結果: {predicted_class} (信頼度: {confidence:.4f})\n")
        sys.stderr.flush()
        
        return predicted_class, confidence
    
    except Exception as e:
        sys.stderr.write(f"予測エラー: {e}\n")
        sys.stderr.flush()
        return None, None
        
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            employee_id = request.form.get('employee_id')
            user_password = request.form.get('password')

            sys.stderr.write(f"\nフォーム入力 - employee_id: {employee_id}, password: {user_password}\n")
            sys.stderr.flush()

            user = None
            try:
                sys.stderr.write(f"DB検索開始: employee_id={int(employee_id)}\n")
                sys.stderr.flush()
                user = User.query.filter_by(employee_id=int(employee_id)).first()
                sys.stderr.write(f"DB検索結果: user={user}\n")
                if user:
                    sys.stderr.write(f"  DB employee_id: {user.employee_id}\n")
                    sys.stderr.write(f"  DB password: {user.password}\n")
                sys.stderr.flush()
            except Exception as e:
                sys.stderr.write(f"クエリエラー: {e}\n")
                sys.stderr.flush()

            sys.stderr.write(f"認証判定:\n")
            sys.stderr.write(f"  user is not None: {user is not None}\n")
            if user:
                sys.stderr.write(f"  パスワード一致: {user_password} == {user.password} → {user_password == user.password}\n")
            sys.stderr.flush()

            if user and user_password == user.password:
                session['user_id'] = user.employee_id
                session['user_password'] = user.password
                session['user_name'] = user.name
                sys.stderr.write(f"認証成功！ /home にリダイレクト\n")
                sys.stderr.flush()
                return redirect(url_for('home'))
            else:
                sys.stderr.write(f"認証失敗\n")
                sys.stderr.flush()
                return render_template('Login.html', error="ユーザー名またはパスワードが正しくありません")
        except Exception as e:
            sys.stderr.write(f"エラー発生: {e}\n")
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


#apiエンドポイント　スマホから送られてきた写真を受け取り、サーバーに保存し、DBを更新する
#画像ファイルはサーバーのフォルダに保存して、dbにはファイルの名前とパスを保存する
@app.route('/api/inspection/<int:inspection_id>/upload_photo', methods=['POST'])
def upload_photo(inspection_id):
    try:
        #クライアントから送られてきたJSONデータを取得
        data = request.get_json()

        if not data:
            return jsonify({'error': 'JSONデータが入っていません'}), 400

        #JSONデータから画像データとファイル名を取得
        photo_data = data.get('photo_data')
        filename = data.get('filename', f'inspection_{inspection_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')

        if not photo_data:
            return jsonify({'error': '画像データがありません'}), 400

        #Base64形式で送られてくるので , より後ろ(実際の画像データ)のみ取り出す
        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]

        #Base64はテキスト形式で画像データを表現したものなので、b64decode()でそれをバイナリデータ(0 or 1)に変換する
        image_binary = base64.b64decode(photo_data)

        #サーバーのstatic/uploadsフォルダに画像を保存する
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        # フォルダが存在しない場合は作成する
        os.makedirs(upload_dir, exist_ok=True)
        #ファイルパスを作成
        filepath = os.path.join(upload_dir, filename)

        #バイナリデータをファイルに書き込む
        #ファイルをwbモード(バイナリ書き込みモード)で開く
        #f.write()でバイナリデータを書き込む
        #with文を使うことで、ファイルのクローズ処理を自動で行う
        with open(filepath, 'wb') as f:
            f.write(image_binary)

        sys.stderr.write(f"画像保存成功: {filepath}\n")
        sys.stderr.write(f"ファイルサイズ: {len(image_binary)} bytes\n")
        sys.stderr.flush()


        # DB更新処理
        # Inspectionテーブルから、このinspection_idに対応する該当レコードを取得して、画像ファイル名とパスを更新する
        inspection = Inspection.query.get(inspection_id)
        #ファイルの名前、ウェブブラウザからアクセスするためのURLパス、アップロード日時を更新
        if inspection:
            inspection.photo_filename = filename
            inspection.image_url = f'/static/uploads/{filename}'
            inspection.photo_uploaded_at = datetime.now()
            #dbに変更をコミット
            db.session.commit()
            sys.stderr.write(f" DB更新成功: inspection_id={inspection_id}, filename={filename}\n")
            sys.stderr.flush()
        else:
            sys.stderr.write(f"Inspection ID {inspection_id} がDBに存在しません\n")
            sys.stderr.flush()
            return jsonify({'error': '検査記録が見つかりません'}), 404

        # 成功レスポンスを返す
        return jsonify({
            'success': True,
            'message': 'Photo uploaded and saved to database',
            'inspection_id': inspection_id,
            'filename': filename,
            'filepath': f'/static/uploads/{filename}'
        }), 200

    # エラーハンドリング
    except Exception as e:
        sys.stderr.write(f"エラー発生: {str(e)}\n")
        sys.stderr.flush()
        return jsonify({'error': str(e), 'message': 'Failed to upload photo'}), 500
    
#DBからinspection_idに対応する検査記録を取得して、ブラウザ上に返すAPIエンドポイント
@app.route('/api/inspection/<int:inspection_id>', methods=['GET'])
def get_inspection(inspection_id):
    try:
        # 指定されたinspection_idに対応する検査記録をDBから取得し、inspection変数に格納
        inspection = Inspection.query.get(inspection_id)
        if not inspection:
            return jsonify({'error': 'Inspection not found'}), 404

        # Enum型は文字列に変換
        chain_grade = inspection.result or inspection.overall_result
        if chain_grade is not None:
            # Enumの場合はname属性を使い、そうでなければそのまま文字列化
            chain_grade = str(chain_grade.name) if hasattr(chain_grade, 'name') else str(chain_grade)

        # 取得した検査記録の情報をJSON形式で返す
        return jsonify({
            'inspection_id': inspection.inspection_id,
            'chain_grade': chain_grade,
            'inspection_date': inspection.inspection_date.strftime("%Y-%m-%d") if inspection.inspection_date else None,
            'photo_filename': inspection.photo_filename,
            'image_url': inspection.image_url
        }), 200

    # エラーハンドリング
    except Exception as e:
        sys.stderr.write(f" /api/inspection/{inspection_id} API エラー: {str(e)}\n")
        sys.stderr.flush()
        return jsonify({'error': str(e)}), 500

# DB初期化チェック
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
