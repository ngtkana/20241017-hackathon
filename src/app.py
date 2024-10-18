import pandas as pd
import os
from flask import Flask, render_template_string

# Flaskアプリの設定
app = Flask(__name__)

# CSVファイルのパス
csv_file_path = 'output/011dd18a-c571-4826-be22-f8be5e07cf1e/DueDate.csv'
image_directory = 'input/011dd18a-c571-4826-be22-f8be5e07cf1e/DueDate/'

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
            <h2>Image Name: {{ row['image_name'] }}</h2>
            <img src="{{ row['image_path'] }}" alt="{{ row['image_name'] }}">
            <p>Original: {{ row['original'] }}</p>
            <p>Corrected: {{ row['corrected'] }}</p>
        </div>
    {% endfor %}
</body>
</html>
'''

@app.route('/')
def index():
    # 各レコードに対して画像のパスを追加
    data['image_path'] = data['image_name'].apply(lambda x: os.path.join(image_directory, x + '.png'))
    
    # HTMLをレンダリング
    return render_template_string(html_template, records=data)

if __name__ == '__main__':
    app.run(debug=True)
import pandas as pd
import os
from flask import Flask, render_template_string

# Flaskアプリの設定
app = Flask(__name__)

# CSVファイルのパス
csv_file_path = 'output/011dd18a-c571-4826-be22-f8be5e07cf1e/DueDate.csv'
image_directory = 'input/011dd18a-c571-4826-be22-f8be5e07cf1e/DueDate/'

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
            <h2>Image Name: {{ row['image_name'] }}</h2>
            <img src="{{ row['image_path'] }}" alt="{{ row['image_name'] }}">
            <p>Original: {{ row['original'] }}</p>
            <p>Corrected: {{ row['corrected'] }}</p>
        </div>
    {% endfor %}
</body>
</html>
'''

@app.route('/')
def index():
    # 各レコードに対して画像のパスを追加
    data['image_path'] = data['image_name'].apply(lambda x: os.path.join(image_directory, x + '.png'))
    
    # HTMLをレンダリング
    return render_template_string(html_template, records=data)

if __name__ == '__main__':
    app.run(debug=True)
