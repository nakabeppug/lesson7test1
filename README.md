# QRコード生成ツール（最小構成）

フォームに入力したテキストからQRコード（PNG）を生成し、画面表示・ダウンロードできます。  
Renderでそのまま公開できる最小構成です。

---

## ローカル実行

```bash
python -m venv env
source env/bin/activate   # Windows: env\Scripts\activate
pip install -r requirements.txt
python app.py
