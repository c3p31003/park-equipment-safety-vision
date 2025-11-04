from flask import Flask, request, jsonify
from PIL import Image
import io

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return "No image part", 400

    file = request.files["image"]
    if file.filename == "":
        return "No selected file", 400

    # 画像を開く（必要に応じて処理を追加）
    image = Image.open(file.stream)
    # TODO: ここで実際に計測や解析する
    # 例としてダミーの結果を返す
    result = "長さ: 123.4 mm"

    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
