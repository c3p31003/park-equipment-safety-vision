# preprocess.py
import cv2
import os
import numpy as np
from utils import load_image, save_image, ensure_dir  # 共通関数

def preprocess_images(input_dir, output_dir):
  ensure_dir(output_dir)

  for filename in os.listdir(input_dir):
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
      continue


    path = os.path.join(input_dir, filename)
    img = load_image(path)
    if img is None:
      print(f"読み込み失敗: {filename}")
      continue

    # サイズ統一
    img = cv2.resize(img, (256, 256))

    # 明るさ補正
    img = cv2.convertScaleAbs(img, alpha=1.2, beta=15)

    # ノイズ除去
    img = cv2.GaussianBlur(img, (3, 3), 0)
    

    save_path = os.path.join(output_dir, filename)
    save_image(save_path, img)

    print(f"前処理完了: {filename}")