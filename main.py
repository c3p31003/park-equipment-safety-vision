from preprocess import preprocess_images
#from mask_generator import generate_masks
from part_detection import detect_parts
#from degradation_detection import detect_degradation

def main():
    print("=== 劣化診断 開始 ===")

    # ① 前処理（明るさ補正など）
    preprocess_images("data/raw", "data/preprocessed")

    # ② マスク生成（背景除去）
    #generate_masks("data/preprocessed", "data/masks")

    # ③ 部位分類（柱・チェーン・座面）
    detect_parts("data/masks", "data/parts")

    # ④ 劣化診断
    #detect_degradation("data/parts", "output/degradation_maps")

    print("=== 全処理完了 ===")

if __name__ == "__main__":
    main()
