from PIL import Image, ImageEnhance, ImageFilter
import os
import glob
import numpy as np
from sklearn.model_selection import train_test_split

# ============================================================
# パーツ定義
# ============================================================

PARTS_CONFIG = {
    'chain': {
        'folder': './dataset/chain/',
        'classes': ['A', 'rust/B', 'rust/C'],
        'class_names': ['normal', 'rust_B', 'rust_C'],
        'output_file': 'chain_undersampled.npz'
    },
    'joint': {
        'folder': './dataset/joint/',
        'classes': ['A', 'rust/B', 'rust/C'],
        'class_names': ['normal', 'rust_B', 'rust_C'],
        'output_file': 'joint_undersampled.npz'
    },
    'pole': {
        'folder': './dataset/pole/',
        'classes': ['A', 'rust/B', 'rust/C'],
        'class_names': ['normal', 'rust_B', 'rust_C'],
        'output_file': 'pole_undersampled.npz'
    },
    'seat': {
        'folder': './dataset/seat/',
        'classes': ['A', 'rust/B', 'rust/C', 'crack/B', 'crack/C'],
        'class_names': ['normal', 'rust_B', 'rust_C', 'crack_B', 'crack_C'],
        'output_file': 'seat_undersampled.npz'
    }
}

image_size = 64
test_ratio = 0.2

# ============================================================
# データ拡張関数
# ============================================================

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
    
    return augmented_data, augmented_labels

# ============================================================
# メイン処理関数
# ============================================================

def process_part(part_name, config):
    """
    1つのパーツの処理
    【修正点】
    - undersampled_indices と undersampled_labels を分離して管理
    - ラベル対応を明示的に保持
    """
    print(f"\n{'='*70}")
    print(f"Processing: {part_name.upper()}")
    print(f"{'='*70}")
    
    # ============================================================
    # ステップ1：画像読み込み
    # ============================================================
    
    print(f"\n=== Loading Images for {part_name} ===")
    
    all_images = []
    all_labels = []
    num_classes = len(config['classes'])
    
    for class_idx, class_folder in enumerate(config['classes']):
        class_name = config['class_names'][class_idx]
        photos_dir = config['folder'] + class_folder
        
        extensions = ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.png', '*.PNG']
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(photos_dir, ext)))
        
        print(f"Class {class_idx} ({class_name}): {len(files)} images from {photos_dir}")
        
        if len(files) == 0:
            print(f"  ⚠ WARNING: No images found in {os.path.abspath(photos_dir)}")
            continue
        
        for file in files:
            try:
                image = Image.open(file)
                image = image.convert("RGB")
                image = image.resize((image_size, image_size), Image.LANCZOS)
                image = image.filter(ImageFilter.SHARPEN)
                
                data = np.asarray(image)
                all_images.append(data)
                all_labels.append(class_idx)
            
            except Exception as e:
                print(f"Error processing {file}: {e}")
                continue
    
    all_images = np.array(all_images, dtype=np.float32)
    all_labels = np.array(all_labels, dtype=np.int32)
    
    if len(all_images) == 0:
        print(f"❌ ERROR: No images found for {part_name}!")
        return False
    
    print(f"\n✓ Total images loaded: {len(all_images)}")
    for class_idx in range(num_classes):
        count = np.sum(all_labels == class_idx)
        print(f"  - Class {class_idx} ({config['class_names'][class_idx]}): {count}")
    
    # ============================================================
    # ステップ2：Train/Test 分割
    # ============================================================
    
    print(f"\n=== Train/Test Split ===")
    
    indices = np.arange(len(all_images))
    train_indices, test_indices = train_test_split(
        indices,
        test_size=test_ratio,
        stratify=all_labels,
        random_state=42
    )
    
    train_labels = all_labels[train_indices]
    
    print(f"Training samples: {len(train_indices)}")
    print(f"Test samples: {len(test_indices)}")
    
    # ============================================================
    # ステップ3：アンダーサンプリング【修正版】
    # ============================================================
    
    print(f"\n=== Undersampling ===")
    
    # 各クラスのカウント
    class_counts = {}
    for class_idx in range(num_classes):
        count = np.sum(train_labels == class_idx)
        class_counts[class_idx] = count
        print(f"Class {class_idx}: {count} images")
    
    min_samples = min(class_counts.values())
    print(f"\nMinimum samples: {min_samples}")
    print(f"Will undersample all classes to: {min_samples} samples")
    
    # 【修正点】アンダーサンプリング後のインデックスとラベルを別々に管理
    undersampled_indices = []
    undersampled_labels = []
    
    for class_idx in range(num_classes):
        class_mask = train_labels == class_idx
        class_indices = np.where(class_mask)[0]
        
        selected = np.random.choice(
            class_indices,
            size=min_samples,
            replace=False
        )
        
        undersampled_indices.extend(selected)
        undersampled_labels.extend([class_idx] * len(selected))
        
        print(f"  Class {class_idx}: selected {len(selected)} from {len(class_indices)}")
    
    undersampled_indices = np.array(undersampled_indices)
    undersampled_labels = np.array(undersampled_labels, dtype=np.int32)
    
    print(f"\n✓ Total undersampled training images: {len(undersampled_indices)}")
    
    # 検証：各クラスのカウント
    for class_idx in range(num_classes):
        count = np.sum(undersampled_labels == class_idx)
        print(f"  - Class {class_idx} after undersampling: {count}")
    
    # ============================================================
    # ステップ4：データ拡張【修正版】
    # ============================================================
    
    print(f"\n=== Augmenting Training Data (10x per image) ===")
    
    X_train = []
    Y_train = []
    
    for i, (idx, label) in enumerate(zip(undersampled_indices, undersampled_labels)):
        if (i + 1) % 50 == 0 or (i + 1) == len(undersampled_indices):
            print(f"Processing: {i + 1}/{len(undersampled_indices)} images...")
        
        img_data = all_images[idx]
        
        # 【修正点】explicit に label を使う（all_labels[idx] から再取得しない）
        X_train.append(img_data)
        Y_train.append(label)
        
        # 拡張
        img_pil = Image.fromarray(img_data.astype(np.uint8))
        aug_data, aug_labels = augment_image_fast(img_pil, label)
        
        X_train.extend(aug_data)
        Y_train.extend(aug_labels)
    
    x_train = np.array(X_train, dtype=np.float32)
    y_train = np.array(Y_train, dtype=np.int32)
    
    # テストデータ
    x_test = all_images[test_indices].astype(np.float32)
    y_test = all_labels[test_indices].astype(np.int32)
    
    # 正規化
    x_train = x_train / 255.0
    x_test = x_test / 255.0
    
    # ============================================================
    # ステップ5：検証＆保存
    # ============================================================
    
    print(f"\n=== Final Dataset Summary ({part_name}) ===")
    print(f"Training data shape: {x_train.shape}")
    
    train_class_counts = {}
    for class_idx in range(num_classes):
        count = np.sum(y_train == class_idx)
        train_class_counts[class_idx] = count
        print(f"  - Class {class_idx} ({config['class_names'][class_idx]}): {count}")
    
    print(f"Test data shape: {x_test.shape}")
    for class_idx in range(num_classes):
        count = np.sum(y_test == class_idx)
        print(f"  - Class {class_idx} ({config['class_names'][class_idx]}): {count}")
    
    print(f"Augmentation ratio: {len(X_train) / len(undersampled_indices):.1f}x per image")
    file_size_mb = (x_train.nbytes + x_test.nbytes) / (1024**2)
    print(f"Estimated file size: {file_size_mb:.1f} MB")
    
    # 【検証】各クラスが大体均衡しているか
    expected_count = train_class_counts[0]
    balanced = all(
        abs(train_class_counts[class_idx] - expected_count) <= 20
        for class_idx in range(num_classes)
    )
    
    if balanced:
        print(f"\n✓ Classes are well-balanced!")
    else:
        print(f"\n⚠ WARNING: Classes may not be balanced")
        for class_idx in range(num_classes):
            ratio = train_class_counts[class_idx] / expected_count
            print(f"  Class {class_idx}: {ratio:.2f}x of expected")
    
    print(f"\nSaving data to '{config['output_file']}'...")
    np.savez(config['output_file'],
             x_train=x_train,
             x_test=x_test,
             y_train=y_train,
             y_test=y_test)
    
    print(f"✓ npz file saved: {config['output_file']}")
    
    return True

# ============================================================
# メイン
# ============================================================

if __name__ == '__main__':
    print("="*70)
    print("Dataset Preparation: All Parts with Undersampling & Augmentation")
    print("="*70)
    
    results = {}
    for part_name, config in PARTS_CONFIG.items():
        try:
            success = process_part(part_name, config)
            results[part_name] = success
        except Exception as e:
            print(f"\n❌ Error processing {part_name}: {e}")
            import traceback
            traceback.print_exc()
            results[part_name] = False
    
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    for part_name, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{part_name}: {status}")
    
    print("\nNext steps:")
    print("  1. Verify the class balance in output")
    print("  2. Check the .npz files in current directory")
    print("  3. Train separate models for each part")