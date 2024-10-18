import pandas as pd
import os
from flask import Flask, render_template_string, send_from_directory

# Flaskアプリの設定
app = Flask(__name__)

# CSVファイルのパス
csv_file_path = 'output/011dd18a-c571-4826-be22-f8be5e07cf1e/DueDate.csv'
image_directory = os.path.abspath('input/011dd18a-c571-4826-be22-f8be5e07cf1e/DueDate/')

# CSVを読み込む
data = pd.read_csv(csv_file_path)

# HTMLテンプレート
html_template = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Due Date Records</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .record { margin-bottom: 20px; }
        img { max-width: 200px; }
    </style>
</head>
<body>
    <h1>Due Date Records</h1>
    {% for index, row in records.iterrows() %}
        <div class="record">
            <h2>{{ row['image_name'] }}</h2>
            <img src="{{ url_for('serve_image', filename=row['image_name'] + '.png') }}" alt="{{ row['image_name'] }}">
            <p>{{ row['original'] }} → {{ row['corrected'] }}</p>
        </div>
    {% endfor %}
</body>
</html>
'''

@app.route('/')
def index():
    # HTMLをレンダリング
    return render_template_string(html_template, records=data)

# 画像をサーブするエンドポイント
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(image_directory, filename)

if __name__ == '__main__':
    app.run(debug=True)

