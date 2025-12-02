# degradation_report.py
import os
import json

def generate_degradation_report(results, report_dir):
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "degradation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"レポート生成完了 → {report_path}")
