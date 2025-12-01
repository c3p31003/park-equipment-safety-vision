from PIL import Image, ImageEnhance, ImageFilter
import os
import glob
import numpy as np
from sklearn.model_selection import train_test_split

classes = ['nomal', 'rust','cracks']
num_classes = len(classes)

# 画像サイズ
image_size = 64
# テスト:訓練 = 2:8 の比率
test_ratio = 0.2

# 画像データを格納
all_images = []
all_labels = []

def augment_image_fast(image, index):
    """高速データ拡張(10倍程度)"""
    augmented_data = []
    augmented_labels = []
    
    # 1. 回転: 5パターン
    for angle in [-15, -7, 0, 7, 15]:
        img_r = image.rotate(angle, expand=False, fillcolor=(0, 0, 0))
        augmented_data.append(np.asarray(img_r))
        augmented_labels.append(index)
    
    # 2. 左右反転
    img_flip_lr = image.transpose(Image.FLIP_LEFT_RIGHT)
    augmented_data.append(np.asarray(img_flip_lr))
    augmented_labels.append(index)
    
    # 3. 明るさ調整: 2パターン
    for brightness_factor in [0.8, 1.2]:
        enhancer = ImageEnhance.Brightness(image)
        img_bright = enhancer.enhance(brightness_factor)
        augmented_data.append(np.asarray(img_bright))
        augmented_labels.append(index)
    
    # 4. コントラスト調整: 2パターン
    for contrast_factor in [0.8, 1.2]:
        enhancer = ImageEnhance.Contrast(image)
        img_contrast = enhancer.enhance(contrast_factor)
        augmented_data.append(np.asarray(img_contrast))
        augmented_labels.append(index)
    
    # 合計: 5 + 1 + 2 + 2 = 10倍
    
    return augmented_data, augmented_labels

# 画像の読み込み(まず全データを読み込み)
print("=== Loading Images ===")
for index, classlabel in enumerate(classes):
    photos_dir = './dataset/seat/' + classlabel
    
    # 複数の拡張子に対応
    extensions = ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.png', '*.PNG']
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(photos_dir, ext)))
    
    print(f"Class: {classlabel}")
    print(f"  Directory: {os.path.abspath(photos_dir)}")
    print(f"  Found {len(files)} images")
    
    if len(files) == 0:
        print(f"  ⚠ WARNING: No images found in {os.path.abspath(photos_dir)}")
        print(f"  Please check:")
        print(f"    1. Folder exists: {os.path.exists(photos_dir)}")
        print(f"    2. Contains image files (.jpg, .jpeg, .png)")
        continue
    
    for i, file in enumerate(files):
        try:
            image = Image.open(file)
            # RGBに変換
            image = image.convert("RGB")
            # 高品質リサイズ(LANCZOSフィルタ使用)
            image = image.resize((image_size, image_size), Image.LANCZOS)
            
            # シャープネスフィルタで鮮明化
            image = image.filter(ImageFilter.SHARPEN)
            
            data = np.asarray(image)
            
            all_images.append(data)
            all_labels.append(index)
        
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

# NumPy配列に変換
all_images = np.array(all_images, dtype=np.float32)
all_labels = np.array(all_labels, dtype=np.int32)

# 画像が見つからなかった場合はエラー終了
if len(all_images) == 0:
    print("\n❌ ERROR: No images found!")
    print("Please check:")
    print("  1. Image folders exist: './dataset/chain_swing/nomal/' and './dataset/chain_swing/rust/'")
    print("  2. Folders contain image files (.jpg, .jpeg, .png)")
    print(f"  3. Current directory: {os.path.abspath('.')}")
    exit(1)

print(f"\nTotal images loaded: {len(all_images)}")
print(f"  - Class 0 (nomal): {np.sum(all_labels == 0)}")
print(f"  - Class 1 (rust): {np.sum(all_labels == 1)}")

# 訓練/テストデータを分割(stratifyでクラス比率を保持)
indices = np.arange(len(all_images))
train_indices, test_indices = train_test_split(
    indices, 
    test_size=test_ratio, 
    stratify=all_labels,
    random_state=42
)

print(f"\n=== Data Split ===")
print(f"Training samples: {len(train_indices)}")
print(f"Test samples: {len(test_indices)}")

# テストデータ(拡張なし)
X_test = all_images[test_indices]
Y_test = all_labels[test_indices]

# 訓練データ(拡張あり)
X_train = []
Y_train = []

print("\n=== Augmenting Training Data (Fast Mode) ===")
print("Augmentation: 10x per image")

for i, idx in enumerate(train_indices):
    if (i + 1) % 100 == 0:
        print(f"Processing: {i + 1}/{len(train_indices)} images...")
    
    img_data = all_images[idx]
    label = all_labels[idx]
    
    # 元画像を追加
    X_train.append(img_data)
    Y_train.append(label)
    
    # PIL Imageに戻して拡張
    img_pil = Image.fromarray(img_data.astype(np.uint8))
    aug_data, aug_labels = augment_image_fast(img_pil, label)
    
    X_train.extend(aug_data)
    Y_train.extend(aug_labels)

print(f"Processing: {len(train_indices)}/{len(train_indices)} images... Done!")

# NumPy配列に変換
x_train = np.array(X_train, dtype=np.float32)
x_test = np.array(X_test, dtype=np.float32)
y_train = np.array(Y_train, dtype=np.int32)
y_test = np.array(Y_test, dtype=np.int32)

# 正規化(0-1の範囲に)
x_train = x_train / 255.0
x_test = x_test / 255.0

print(f"\n=== Final Dataset Summary ===")
print(f"Training data: {x_train.shape}")
print(f"  - Class 0: {np.sum(y_train == 0)}")
print(f"  - Class 1: {np.sum(y_train == 1)}")
print(f"Test data: {x_test.shape}")
print(f"  - Class 0: {np.sum(y_test == 0)}")
print(f"  - Class 1: {np.sum(y_test == 1)}")
print(f"Augmentation ratio: {len(X_train) / len(train_indices):.1f}x per image")
print(f"Estimated file size: {(x_train.nbytes + x_test.nbytes) / (1024**2):.1f} MB")

# 保存
print("\nSaving data...")
np.savez('./seat_aug_improved.npz', 
        x_train=x_train, 
        x_test=x_test, 
        y_train=y_train, 
        y_test=y_test)

print("npzファイルが保存されました。 'seat_aug_improved.npz'")
print("\nNext step: Run 'python train_model.py' to train the model")