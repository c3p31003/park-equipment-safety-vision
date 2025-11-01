# part_detection.py
import os
import shutil
from utils import ensure_dir, list_images  # 共通関数

def detect_parts(input_dir, output_dir):
    """
    ファイル名の頭文字に基づいて分類
    """
    part_map = {
        "p": "pillar",
        "c": "chain",
        "s": "seat",
    }

    # 出力ディレクトリの作成
    for part in list(part_map.values()) + ["unknown"]:
        ensure_dir(os.path.join(output_dir, part))

    # 入力ディレクトリ内の画像一覧
    image_files = list_images(input_dir)

    for img_path in image_files:
        filename = os.path.basename(img_path)
        prefix = filename[0].lower()

        # 頭文字に対応する部位を判定
        part = part_map.get(prefix, "unknown")

        dst_dir = os.path.join(output_dir, part)
        dst_path = os.path.join(dst_dir, filename)

        # ファイルコピー（メタデータ保持）
        shutil.copy2(img_path, dst_path)
        print(f"部位抽出完了: {filename} -> {part}")