import datetime
from threading import Thread
from flask import Flask, render_template_string

app = Flask("")

# サービス状況を確認できるHTMLデザイン
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Discord Bot Status</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: #f0f2f5;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }
        h1 {
            color: #2c3e50;
            font-size: 1.5rem;
            margin-bottom: 10px;
        }
        .status-badge {
            display: inline-block;
            background-color: #d4edda;
            color: #155724;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9rem;
            margin: 15px 0;
        }
        p {
            color: #666;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        .time {
            margin-top: 20px;
            font-size: 0.8rem;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>🌤️ Discord Weather Bot</h1>
        <div class="status-badge">● サービス稼働中 (Online)</div>
        <p>Render上でBotと通信サーバーが正常にオンライン状態を維持しています。</p>
        <div class="time">確認日時: {{ current_time }}</div>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
  current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  return render_template_string(HTML_TEMPLATE, current_time=current_time)


def run():
  app.run(host="0.0.0.0", port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()
