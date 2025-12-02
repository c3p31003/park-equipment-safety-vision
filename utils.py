# utils.py
import cv2
import os

def ensure_dir(path):
    """指定フォルダがなければ作成"""
    if not os.path.exists(path):
        os.makedirs(path)

def load_image(path):
    """画像読み込み"""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"画像読み込み失敗: {path}")
    return img

def save_image(path, img):
    """画像保存"""
    cv2.imwrite(path, img)
