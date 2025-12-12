import os
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
import cv2

# --------------------------
# Simple UNet モデル定義
# --------------------------
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
            nn.ConvTranspose2d(16, num_classes, 2, stride=2)
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

# --------------------------
# Noise 推定 (微細汚れ)
# --------------------------
def estimate_noise_level(image_array):
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    noise_score = np.mean(np.abs(lap))

    # 最大値を93%、最小値0.3%でクリップ
    noise_ratio = min(noise_score / 50.0 * 100.0, 93.0)
    noise_ratio = max(noise_ratio, 0.3)
    return noise_ratio

# --------------------------
# 劣化度計算
# --------------------------
def calculate_degradation(mask_array, rust_id=3):
    total_fg = np.sum(mask_array != 0)
    rust_pixels = np.sum(mask_array == rust_id)
    if total_fg == 0:
        return 0.0, False
    degradation = (rust_pixels / total_fg) * 100.0
    degradation = min(degradation, 93.0)  # 安全のため上限
    return degradation, rust_pixels > 0

# --------------------------
# 推論本体
# --------------------------
def run_inference(
    image_path,
    model_path="models/best_part_segmenter.pth",
    num_classes=5,
    rust_id=3,
    save_output=False
):
    import torch.nn.functional as F

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
        transforms.Resize((128, 128), interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.ToTensor()
    ])
    input_tensor = preprocess(input_image).unsqueeze(0).to(device)

    # --- 推論 ---
    with torch.no_grad():
        output = model(input_tensor)

    # --- マスク生成 ---
    probs = F.softmax(output, dim=1)
    _, predicted_mask = torch.max(probs, 1)
    mask_array = predicted_mask.squeeze().cpu().numpy()

    # foreground判定
    fg_mask = mask_array != 0
    total_fg_pixels = int(np.sum(fg_mask))
    rust_pixels = int(np.sum(mask_array == rust_id))

    # 異常ケース: foregroundが極端に少ない場合
    if total_fg_pixels < 10:
        degradation_ratio = estimate_noise_level(original_img_array)
        has_rust = False
    else:
        degradation_ratio = (rust_pixels / total_fg_pixels) * 100.0
        degradation_ratio = min(degradation_ratio, 93.0)  # 上限
        has_rust = rust_pixels > 0

    # rustゼロならノイズ推定
    if not has_rust:
        degradation_ratio = estimate_noise_level(original_img_array)

    # 0〜93% にクリップ
    degradation_ratio = min(max(degradation_ratio, 0.0), 93.0)

    # --- 保存処理 ---
    bg_removed_path = None
    rust_mask_path = None
    if save_output:
        mask_img = Image.fromarray(mask_array.astype(np.uint8), mode='L')
        mask_img_resized = mask_img.resize(original_size, Image.NEAREST)
        mask_array_resized = np.array(mask_img_resized)

        foreground_mask = mask_array_resized != 0
        background_removed_array = original_img_array * foreground_mask[:, :, None]

        output_dir = os.path.join("output", "results")
        os.makedirs(output_dir, exist_ok=True)

        base = os.path.basename(image_path)
        stem, _ = os.path.splitext(base)

        bg_removed_path = os.path.join(output_dir, f"{stem}_bg_removed.png")
        rust_mask_path = os.path.join(output_dir, f"{stem}_rust_mask.png")

        Image.fromarray(background_removed_array.astype(np.uint8)).save(bg_removed_path)
        rust_mask_out = (mask_array_resized == rust_id).astype(np.uint8) * 255
        Image.fromarray(rust_mask_out).save(rust_mask_path)

    return float(round(degradation_ratio, 2)), bg_removed_path, rust_mask_path
