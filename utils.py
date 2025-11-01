import os
import cv2

def ensure_dir(path):
    """フォルダが存在しなければ作成"""
    os.makedirs(path, exist_ok=True)

def list_images(directory):
    """ディレクトリ内の画像ファイル一覧を返す"""
    valid_ext = (".jpg", ".jpeg", ".png")
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(valid_ext)
    ]

def load_image(path):
    """画像を読み込み（失敗時はNone）"""
    img = cv2.imread(path)
    if img is None:
        print(f"読み込み失敗: {path}")
    return img

def save_image(path, img):
    """画像を保存（途中のフォルダも自動作成）"""
    ensure_dir(os.path.dirname(path))
    cv2.imwrite(path, img)
