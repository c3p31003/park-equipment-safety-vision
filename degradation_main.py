# degradation_main.py（Web用に最適化＆単体実行可）
import os
import json
from inference_and_diagnosis import run_inference

INPUT_DIR = "data/raw"  # 最新アップロード画像が置かれるフォルダ
OUTPUT_REPORT = "output/reports/degradation_report.json"
THRESHOLD = 0.5  # 0.5%以上 → NG

os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)

def get_latest_degradation():
    """
    最新画像を解析し、劣化度を返す
    :return: (degradation_ratio: float, filename: str) or (None, None)
    """
    # フォルダ内の画像一覧
    images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not images:
        return None, None

    latest_file = sorted(images)[-1]
    image_path = os.path.join(INPUT_DIR, latest_file)

    try:
        degradation_ratio, bg_path, rust_mask_path = run_inference(image_path)

        report = {
            "filename": latest_file,
            "degradation_ratio": round(degradation_ratio, 2),
            "bg_removed": bg_path,
            "rust_mask": rust_mask_path,
            "判定": "NG" if degradation_ratio >= THRESHOLD else "OK"
        }

        # JSON 保存
        with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return round(degradation_ratio, 2), latest_file

    except Exception as e:
        print(f" エラー: {e}")
        return None, None

# 単体テスト実行用
if __name__ == "__main__":
    deg, fname = get_latest_degradation()
    if deg is not None:
        print(f"最新画像: {fname} → 劣化度: {deg}%")
    else:
        print("画像がありません")
