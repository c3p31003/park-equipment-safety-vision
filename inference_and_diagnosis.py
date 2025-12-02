import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import numpy as np
import os
import cv2

# ----------------------------------------
# 1. モデル構造（学習時と同じ）
# ----------------------------------------
class SimpleUNet(nn.Module):
    def __init__(self, num_classes=5): 
        super(SimpleUNet, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(32, 16, 2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(16, num_classes, 2, stride=2),
        )
    
    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x 


# ----------------------------------------
# 2. Noise（微細汚れ）推定
# ----------------------------------------
def estimate_noise_level(image_array):
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    noise_score = np.mean(np.abs(lap))
    normalized = noise_score / 50.0
    noise_level = max(0.3, min(normalized, 2.0))
    return noise_level


# ----------------------------------------
# 3. 劣化度計算
# ----------------------------------------
def calculate_degradation(mask_array, rust_id=3):
    total_playground_pixels = np.sum(mask_array != 0)
    rust_pixels = np.sum(mask_array == rust_id)
    if total_playground_pixels == 0:
        return 0.0, False
    degradation = (rust_pixels / total_playground_pixels) * 100.0
    has_rust = rust_pixels > 0
    return degradation, has_rust


# ----------------------------------------
# 4. 推論実行（マスク生成＆劣化算出）
# ----------------------------------------
def run_inference(image_path, model_path="models/best_part_segmenter.pth", num_classes=5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # --- モデルロード ---
    model = SimpleUNet(num_classes=num_classes).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    # --- 画像読み込み ---
    input_image = Image.open(image_path).convert("RGB")
    original_size = input_image.size
    original_img_array = np.array(input_image)

    preprocess = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])

    input_tensor = preprocess(input_image).unsqueeze(0).to(device)

    # --- 推論 ---
    with torch.no_grad():
        output = model(input_tensor)

    _, predicted_mask = torch.max(output, 1)
    mask_array = predicted_mask.squeeze().cpu().numpy()

    # --- 下部20%の錆誤検出除去 ---
    H, W = mask_array.shape
    bottom = int(H * 0.8)
    mask_array[bottom:, :][mask_array[bottom:, :] == 3] = 0

    # --- 劣化度計算（錆の有無も返す） ---
    degradation_ratio, has_rust = calculate_degradation(mask_array)

    # ★錆ゼロ → 画像ノイズから微小劣化度を付与
    if not has_rust:
        degradation_ratio = estimate_noise_level(original_img_array)

    # --- 結果画像保存 ---
    mask_img = Image.fromarray(mask_array.astype(np.uint8), mode='L')
    mask_img_resized = mask_img.resize(original_size, Image.NEAREST)
    mask_array_resized = np.array(mask_img_resized)

    original_img_array = np.array(input_image)
    foreground_mask = mask_array_resized != 0
    background_removed_array = original_img_array * foreground_mask[:, :, None]

    # ★ output/results 配下に保存
    output_dir = os.path.join("output", "results")
    os.makedirs(output_dir, exist_ok=True)

    base = os.path.basename(image_path)
    stem, _ = os.path.splitext(base)

    bg_removed_path = os.path.join(output_dir, f"{stem}_bg_removed.png")
    rust_mask_path = os.path.join(output_dir, f"{stem}_rust_mask.png")

    Image.fromarray(background_removed_array.astype(np.uint8)).save(bg_removed_path)
    rust_mask = (mask_array_resized == 3).astype(np.uint8) * 255
    Image.fromarray(rust_mask).save(rust_mask_path)

    return degradation_ratio, bg_removed_path, rust_mask_path
