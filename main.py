import os
import json
from inference_and_diagnosis import run_inference

# 入力フォルダ
INPUT_DIR = "data/raw"

# レポート出力パス
OUTPUT_REPORT = "output/reports/degradation_report.json"
os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)

# -------------------------------
# ⭐ 劣化判定しきい値
#    0.5% 未満 → OK
#    0.5% 以上 → NG
# -------------------------------
THRESHOLD = 0.5

report_data = []

if not os.path.isdir(INPUT_DIR):
    print(f"エラー: 指定されたフォルダ '{INPUT_DIR}' が見つかりません。")
else:
    print(f"--- フォルダ '{INPUT_DIR}' 内の画像に対する診断を開始します ---")
    
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(INPUT_DIR, filename)
            print(f"\n[処理開始] ファイル: {filename}")

            try:
                # run_inference は (ratio, bg_path, rust_mask_path) を返す
                degradation_ratio, bg_path, rust_mask_path = run_inference(image_path)

                # 判定（0.5% 未満は正常扱い）
                verdict = "NG" if degradation_ratio >= THRESHOLD else "OK"

                result = {
                    "filename": filename,
                    "degradation_ratio": round(degradation_ratio, 2),
                    "bg_removed": bg_path,
                    "rust_mask": rust_mask_path,
                    "判定": verdict
                }
                report_data.append(result)

                print(f"{filename} → 劣化度 {result['degradation_ratio']}%, 判定: {verdict}")

            except Exception as e:
                print(f"[エラー] {filename}: {e}")

    # JSON レポート保存
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"\n--- レポート生成完了 → {OUTPUT_REPORT} ---")
    print("\n=== 全処理完了 ===")
