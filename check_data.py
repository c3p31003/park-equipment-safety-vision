import numpy as np

# 訓練データファイルを読み込む
data = np.load('./chain_aug_improved.npz', allow_pickle=True)
print(f"訓練データ形状: {data['x_train'].shape}")
# 出力例：(100, 128, 128, 3) ← この場合、画像サイズは 128x128