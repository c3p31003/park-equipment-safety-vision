# Flask バックエンド実装例
# 既存のFlaskアプリに追加してください

from flask import Flask, request, jsonify
import base64
from datetime import datetime
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# DB接続情報（あなたのRDSに合わせてください）
DB_CONFIG = {
    'host': 'your-rds-endpoint.amazonaws.com',
    'user': 'PE_A01',
    'password': 'your-password',
    'database': 'a01_db'
}

# ============================================================
# 【重要】テーブルスキーマ：事前にこれをMySQLで実行してください
# ============================================================
# CREATE TABLE equipment_photos (
#     photo_id INT AUTO_INCREMENT PRIMARY KEY,
#     equipment_id INT NOT NULL,
#     photo_data LONGBLOB NOT NULL,        # バイナリ画像データ
#     photo_filename VARCHAR(255),         # 元のファイル名
#     uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
# );


def get_db_connection():
    """RDS MySQLへの接続を取得"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None


@app.route('/api/upload_photo', methods=['POST'])
def upload_photo():
    """
    クライアント側から送られてきた画像（Base64）を受け取り、
    MySQLのBLOB型に保存する
    
    【期待されるリクエスト形式】
    {
        "photo_data": "data:image/png;base64,iVBORw0KGgo...",  # Canvas.toDataURL()の出力
        "equipment_id": 1,
        "filename": "inspection_2025-01-15.png"
    }
    """
    try:
        # クライアントからのJSONを取得
        data = request.get_json()
        
        if not data or 'photo_data' not in data:
            return jsonify({"error": "photo_data is required"}), 400
        
        # Base64文字列を抽出
        base64_string = data['photo_data']
        
        # 「data:image/png;base64,」の部分を削除（あれば）
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Base64 → バイナリに変換
        binary_data = base64.b64decode(base64_string)
        
        # DB接続
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = connection.cursor()
        
        # INSERT文で保存
        insert_query = """
            INSERT INTO equipment_photos (equipment_id, photo_data, photo_filename)
            VALUES (%s, %s, %s)
        """
        
        equipment_id = data.get('equipment_id', 1)  # デフォルト値1
        filename = data.get('filename', f'photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        cursor.execute(insert_query, (equipment_id, binary_data, filename))
        connection.commit()
        
        photo_id = cursor.lastrowid  # 挿入されたレコードのID
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "success": True,
            "message": "Photo uploaded successfully",
            "photo_id": photo_id,
            "filename": filename
        }), 200
    
    except Exception as e:
        print(f"Error uploading photo: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/get_photo/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    """
    保存された写真をBinaryで取得（画像表示用）
    """
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = connection.cursor()
        cursor.execute("SELECT photo_data, photo_filename FROM equipment_photos WHERE photo_id = %s", (photo_id,))
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not result:
            return jsonify({"error": "Photo not found"}), 404
        
        binary_data, filename = result
        
        # バイナリ → Base64に変換（必要に応じて）
        base64_data = base64.b64encode(binary_data).decode('utf-8')
        
        return jsonify({
            "photo_id": photo_id,
            "photo_data": f"data:image/png;base64,{base64_data}",
            "filename": filename
        }), 200
    
    except Exception as e:
        print(f"Error retrieving photo: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)