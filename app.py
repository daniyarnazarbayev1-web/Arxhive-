import json
import os
import requests
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

SECRET_CODE = "LOL2010&"
DATA_FILE = "articles.json"

def load_articles():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [{
        "title": "Добро пожаловать в Arxhive",
        "content": "Это первая статья на платформе Arxhive."
    }]

def save_articles(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Ошибка сохранения:", e)

articles = load_articles()

def send_email_request(topic, message):
    url = "https://formspree.io/f/mqakozoy"
    payload = {
        "email": "mokotographic@gmail.com",
        "topic": topic,
        "message": message
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print("Ошибка отправки:", e)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arxhive</title>
    <style>
        body { font-family: Arial, sans-serif; background: #ffffff; color: #222; margin: 0; padding: 0; line-height: 1.6; }
        header { background: #f4f4f4; border-bottom: 2px solid #ddd; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 32px; font-weight: bold; font-family: 'Georgia', serif; }
        nav a { margin-left: 15px; color: #0056b3; text-decoration: none; font-weight: bold; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .card { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 4px; padding: 20px; margin-bottom: 25px; }
        .article-title { margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 8px; }
        form { display: flex; flex-direction: column; gap: 12px; }
        input[type="text"], input[type="password"], textarea { width: 100%; padding: 10px; border: 1px solid #ccc; box-sizing: border-box; }
        textarea { height: 120px; }
        button { background: #28a745; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 3px; align-self: flex-start; }
        .btn-req { background: #007bff; }
    </style>
</head>
<body>

<header>
    <div class="logo" id="dynamicLogo">Arxhive</div>
    <nav>
        <a href="/">Главная</a>
        <a href="#request">Запрос</a>
        <a href="#publish">Публикация</a>
    </nav>
</header>

<div class="container">

    <h2>Статьи</h2>
    {% for article in articles %}
    <div class="card">
        <h3 class="article-title">{{ article.title }}</h3>
        <p>{{ article.content }}</p>
    </div>
    {% endfor %}

    <div id="request" class="card">
        <h2>Запрос на публикацию</h2>
        <form action="/request_article" method="POST">
            <input type="text" name="topic" placeholder="Тема статьи" required>
            <textarea name="message" placeholder="Текст просьбы..." required></textarea>
            <button type="submit" class="btn-req">Отправить запрос</button>
        </form>
    </div>

    <div id="publish" class="card">
        <h2>Добавить статью (Код)</h2>
        <form action="/add_article" method="POST">
            <input type="password" name="code" placeholder="Секретный код" required>
            <input type="text" name="title" placeholder="Заголовок" required>
            <textarea name="content" placeholder="Текст статьи" required></textarea>
            <button type="submit">Опубликовать</button>
        </form>
    </div>

</div>

<script>
    function updateLogoColor() {
        const now = new Date();
        const totalSum = now.getSeconds() + now.getMinutes() + now.getHours() + now.getDate() + (now.getMonth() + 1) + now.getFullYear();
        const hue = totalSum % 360; 
        document.getElementById('dynamicLogo').style.color = `hsl(${hue}, 70%, 40%)`;
    }
    setInterval(updateLogoColor, 1000);
    updateLogoColor();
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, articles=articles)

@app.route('/request_article', methods=['POST'])
def request_article():
    send_email_request(request.form.get('topic'), request.form.get('message'))
    return redirect(url_for('index'))

@app.route('/add_article', methods=['POST'])
def add_article():
    if request.form.get('code') == SECRET_CODE:
        articles.insert(0, {
            "title": request.form.get('title'),
            "content": request.form.get('content')
        })
        save_articles(articles)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
