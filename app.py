import os
import io
import base64
from flask import Flask, request, render_template_string
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

app = Flask(__name__)

# 環境変数 DEBUG が true/1 のときのみデバッグ有効
DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
app.config["DEBUG"] = DEBUG

# 入力制限
MAX_TEXT_LEN = 500
MAX_SIZE = 1024

ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}

HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>QRコード生成ツール</title>
  <style>
    body { font-family: sans-serif; margin: 40px; }
    label { display: block; margin-top: 10px; }
    input, select, textarea { width: 100%; padding: 6px; }
    button { margin-top: 15px; padding: 8px 16px; }
    .error { color: red; margin-top: 10px; }
    .preview { margin-top: 20px; }
  </style>
</head>
<body>
  <h1>QRコード生成ツール</h1>

  <form method="post">
    <label>テキスト（必須）</label>
    <textarea name="text" required>{{ text }}</textarea>

    <label>サイズ（px, 最大1024）</label>
    <input type="number" name="size" value="{{ size }}">

    <label>余白（border）</label>
    <input type="number" name="border" value="{{ border }}">

    <label>誤り訂正レベル</label>
    <select name="error">
      {% for k in ["L","M","Q","H"] %}
      <option value="{{k}}" {% if k == error %}selected{% endif %}>{{k}}</option>
      {% endfor %}
    </select>

    <button type="submit">生成</button>
  </form>

  {% if error_msg %}
    <div class="error">{{ error_msg }}</div>
  {% endif %}

  {% if img_data %}
    <div class="preview">
      <h2>プレビュー</h2>
      <img src="{{ img_data }}" alt="QRコード">
      <p>
        <a href="{{ img_data }}" download="qr.png">PNGをダウンロード</a>
      </p>
    </div>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    img_data = None
    error_msg = None

    # デフォルト値
    text = ""
    size = 300
    border = 4
    error = "M"

    if request.method == "POST":
        try:
            text = request.form.get("text", "").strip()
            size = int(request.form.get("size", size))
            border = int(request.form.get("border", border))
            error = request.form.get("error", error)

            if not text:
                raise ValueError("テキストを入力してください。")
            if len(text) > MAX_TEXT_LEN:
                raise ValueError(f"テキストは最大{MAX_TEXT_LEN}文字までです。")
            if size <= 0 or size > MAX_SIZE:
                raise ValueError(f"サイズは1〜{MAX_SIZE}pxの範囲で指定してください。")
            if border < 0:
                raise ValueError("余白は0以上で指定してください。")
            if error not in ERROR_LEVELS:
                raise ValueError("誤り訂正レベルが不正です。")

            qr = qrcode.QRCode(
                error_correction=ERROR_LEVELS[error],
                box_size=10,
                border=border,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((size, size))

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            b64 = base64.b64encode(buf.read()).decode("ascii")
            img_data = f"data:image/png;base64,{b64}"

        except Exception as e:
            error_msg = str(e)

    return render_template_string(
        HTML,
        img_data=img_data,
        error_msg=error_msg,
        text=text,
        size=size,
        border=border,
        error=error,
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
