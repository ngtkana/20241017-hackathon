from flask import Flask, render_template, send_from_directory
import os
import json

app = Flask(__name__, static_folder="../input", template_folder="../templates")

# 画像と JSON データのベースパス
IMAGE_DIR = "input"
JSON_DIR = "output"

# タスクデータ（与えられたリスト）
tasks = [
    {
        "tenant_id": "fc81fcd7-b4b9-4c75-beda-215b8dcef4e0",
        "attribute": "DrawingNumber",
        "ocr_miss": ["DR-33IWPYQ3WBJ8", "DR-33SE4ABFHVAW", "DR-39HEFFOQJG3S", "DR-3N6MMZMF3M3Q", "DR-3R67OQGM4IZP"],
        "ocr_correct": ["DR-3BSACKHDU3HT", "DR-7PXQ6NPPNUQD", "DR-638WRPMGVZHZ"]
    },
    {
        "tenant_id": "56dde43c-54d4-4775-99e1-d4db86b5a1de",
        "attribute": "DrawingNumber",
        "ocr_miss": ["DR-33MYOREOEPAJ", "DR-36OFOWVKDGQB", "DR-39KSJRJD94M4", "DR-3AVZMC7OIEXG", "DR-3BBHAOTZDYXP"],
        "ocr_correct": ["DR-364QDST4HZP7", "DR-3E8SPKYD8VPS", "DR-3EZWBU7JZ6VS", "DR-3SXE3KMFHEUP"]
    }
]

# 画像を提供するルート
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

# メインページで画像と JSON データを並べて表示
@app.route('/')
def index():
    for task in tasks:
        tenant_id = task['tenant_id']
        for drawing_id in task['ocr_miss']:
            json_path = os.path.join(JSON_DIR, tenant_id, "DrawingNumber", f"{drawing_id}.json")
            with open(json_path) as f:
                task['json_data'] = json.load(f)  # JSON データを事前にロード
    return render_template('index.html', tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)
