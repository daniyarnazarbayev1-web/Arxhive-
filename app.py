import json
import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, jsonify

app = Flask(__name__)

SECRET_ADMIN_PATH = "admin-lol2010"
DATA_FILE = "articles.json"

def load_articles():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for art in data:
                    if "likes" not in art:
                        art["likes"] = 0
                    if "dislikes" not in art:
                        art["dislikes"] = 0
                return data
        except Exception:
            pass
    return [{
        "id": 1,
        "title": "Arxhive Registry Manifesto",
        "date": "2026-09-09",
        "modified": None,
        "content": "Arxhive is a dedicated personal digital repository designed for documenting, archiving, and storing verified textual materials and references.",
        "likes": 0,
        "dislikes": 0
    }]

def save_articles(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Save error:", e)

articles = load_articles()

HTML_PUBLIC = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arxhive — Official Text Repository</title>
    <style>
        body { font-family: 'Georgia', serif; background: #ffffff; color: #111111; margin: 0; padding: 0; line-height: 1.8; }
        header { background: #fafafa; border-bottom: 1px solid #e0e0e0; padding: 25px 40px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 28px; font-weight: bold; letter-spacing: 0.5px; }
        nav a { margin-left: 20px; color: #222222; text-decoration: none; font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; }
        nav a:hover { text-decoration: underline; }
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        .archive-card { background: #ffffff; border: 1px solid #dddddd; padding: 30px; margin-bottom: 35px; }
        .article-meta { font-family: Arial, sans-serif; font-size: 12px; color: #666666; text-transform: uppercase; margin-bottom: 12px; }
        .article-title { margin-top: 0; font-size: 26px; font-weight: normal; color: #000000; border-bottom: 1px solid #eeeeee; padding-bottom: 10px; }
        .article-content { font-size: 16px; color: #222222; white-space: pre-line; }
        .article-modified { font-family: Arial, sans-serif; font-size: 12px; color: #888888; font-style: italic; margin-top: 15px; border-top: 1px dashed #eee; padding-top: 8px; }
        
        .action-bar { display: flex; align-items: center; gap: 10px; margin-top: 20px; font-family: Arial, sans-serif; }
        .vote-btn, .share-btn { background: #f4f4f4; border: 1px solid #cccccc; padding: 6px 14px; font-size: 13px; cursor: pointer; font-weight: bold; }
        .vote-btn:hover, .share-btn:hover { background: #e8e8e8; }
        .vote-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
        footer { font-family: Arial, sans-serif; text-align: center; padding: 30px; border-top: 1px solid #eeeeee; color: #888888; font-size: 12px; margin-top: 60px; }
    </style>
</head>
<body>

<header>
    <div class="logo" id="dynamicLogo">Arxhive</div>
    <nav>
        <a href="/">Archive Index</a>
    </nav>
</header>

<div class="container">

    <div style="margin-bottom: 40px; border-left: 2px solid #111; padding-left: 15px; font-family: Arial, sans-serif;">
        <h1 style="font-size: 22px; margin: 0 0 5px 0; font-weight: bold;">Document Registry</h1>
        <p style="margin: 0; color: #555555; font-size: 13px;">Official archived collection of author statements, documentation, and records.</p>
    </div>

    {% for article in articles %}
    <div class="archive-card" id="article-{{ article.id }}">
        <div class="article-meta">Record #ARX-{{ article.id }} &bull; Published: {{ article.date }}</div>
        <h2 class="article-title">{{ article.title }}</h2>
        <div class="article-content">{{ article.content }}</div>
        
        {% if article.modified %}
        <div class="article-modified">Article was modified on {{ article.modified }} by Administration</div>
        {% endif %}
        
        <div class="action-bar">
            <button class="vote-btn" id="like-btn-{{ article.id }}" onclick="vote('{{ article.id }}', 'like')">👍 <span id="likes-{{ article.id }}">{{ article.likes }}</span></button>
            <button class="vote-btn" id="dislike-btn-{{ article.id }}" onclick="vote('{{ article.id }}', 'dislike')">👎 <span id="dislikes-{{ article.id }}">{{ article.dislikes }}</span></button>
            <button class="share-btn" onclick="copyLink('{{ article.id }}')">Copy Record Link</button>
        </div>
    </div>
    {% endfor %}

</div>

<footer>
    &copy; Arxhive Institutional Repository. All records registered.
</footer>

<script>
    function updateLogoColor() {
        const now = new Date();
        const totalSum = now.getSeconds() + now.getMinutes() + now.getHours() + now.getDate() + (now.getMonth() + 1) + now.getFullYear();
        const hue = totalSum % 360; 
        document.getElementById('dynamicLogo').style.color = `hsl(${hue}, 70%, 35%)`;
    }
    setInterval(updateLogoColor, 1000);
    updateLogoColor();

    function copyLink(id) {
        const url = window.location.origin + '/#article-' + id;
        navigator.clipboard.writeText(url).then(() => {
            alert('Record link copied to clipboard.');
        });
    }

    function checkVotes() {
        {% for article in articles %}
            if (localStorage.getItem('voted_article_{{ article.id }}')) {
                const likeBtn = document.getElementById('like-btn-{{ article.id }}');
                const dislikeBtn = document.getElementById('dislike-btn-{{ article.id }}');
                if (likeBtn) likeBtn.disabled = true;
                if (dislikeBtn) dislikeBtn.disabled = true;
            }
        {% endfor %}
    }

    function vote(id, type) {
        if (localStorage.getItem('voted_article_' + id)) {
            alert('You have already voted on this article.');
            return;
        }

        fetch('/vote/' + id + '/' + type, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('likes-' + id).innerText = data.likes;
                    document.getElementById('dislikes-' + id).innerText = data.dislikes;
                    localStorage.setItem('voted_article_' + id, type);
                    document.getElementById('like-btn-' + id).disabled = true;
                    document.getElementById('dislike-btn-' + id).disabled = true;
                }
            });
    }

    checkVotes();
</script>

</body>
</html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Arxhive — Administrative Control</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; color: #111; margin: 0; padding: 40px; }
        .admin-box { max-width: 750px; margin: 0 auto; background: #fff; border: 1px solid #ccc; padding: 30px; }
        input[type="text"], textarea { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; box-sizing: border-box; font-size: 14px; }
        textarea { height: 160px; }
        button { background: #111; color: white; border: none; padding: 10px 18px; font-size: 14px; cursor: pointer; font-weight: bold; }
        button:hover { background: #333; }
        .article-item { border-bottom: 1px solid #eee; padding: 15px 0; display: flex; justify-content: space-between; align-items: center; }
        .btn-edit { background: #0056b3; text-decoration: none; color: #fff; padding: 5px 10px; font-size: 12px; font-weight: bold; margin-right: 5px; }
        .btn-del { background: #c92a2a; text-decoration: none; color: #fff; padding: 5px 10px; font-size: 12px; font-weight: bold; }
        a { color: #111; }
    </style>
</head>
<body>

<div class="admin-box">
    <h2>Arxhive Administrative Control</h2>
    <p><a href="/">&larr; Return to Public Index</a></p>
    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

    {% if edit_article %}
    <h3>Edit Record #ARX-{{ edit_article.id }}</h3>
    <form action="/update_article/{{ edit_article.id }}" method="POST">
        <label>Title:</label>
        <input type="text" name="title" value="{{ edit_article.title }}" required>
        <label>Content:</label>
        <textarea name="content" required>{{ edit_article.content }}</textarea>
        <button type="submit">Save Changes</button>
        <a href="/{{ admin_path }}" style="margin-left: 10px; font-size: 13px;">Cancel</a>
    </form>
    {% else %}
    <h3>Create New Record</h3>
    <form action="/add_article_internal" method="POST">
        <label>Title:</label>
        <input type="text" name="title" required placeholder="Record title">
        <label>Content:</label>
        <textarea name="content" required placeholder="Record text body..."></textarea>
        <button type="submit">Publish to Archive</button>
    </form>
    {% endif %}

    <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">

    <h3>Manage Existing Records</h3>
    {% for article in articles %}
    <div class="article-item">
        <div>
            <strong>#ARX-{{ article.id }}: {{ article.title }}</strong>
            <br><small style="color: #666;">Date: {{ article.date }} | 👍 {{ article.likes }} | 👎 {{ article.dislikes }}</small>
        </div>
        <div>
            <a href="/{{ admin_path }}?edit={{ article.id }}" class="btn-edit">Edit</a>
            <a href="/delete_article/{{ article.id }}" class="btn-del" onclick="return confirm('Delete this record?')">Delete</a>
        </div>
    </div>
    {% endfor %}
</div>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PUBLIC, articles=articles)

@app.route(f'/{SECRET_ADMIN_PATH}')
def admin_panel():
    edit_id = request.args.get('edit')
    edit_article = None
    if edit_id:
        for art in articles:
            if str(art['id']) == str(edit_id):
                edit_article = art
                break
    return render_template_string(HTML_ADMIN, articles=articles, edit_article=edit_article, admin_path=SECRET_ADMIN_PATH)

@app.route('/vote/<int:article_id>/<type_vote>', methods=['POST'])
def vote(article_id, type_vote):
    for art in articles:
        if art['id'] == article_id:
            if type_vote == 'like':
                art['likes'] += 1
            elif type_vote == 'dislike':
                art['dislikes'] += 1
            save_articles(articles)
            return jsonify({'success': True, 'likes': art['likes'], 'dislikes': art['dislikes']})
    return jsonify({'success': False}), 404

@app.route('/add_article_internal', methods=['POST'])
def add_article_internal():
    title = request.form.get('title')
    content = request.form.get('content')
    
    if title and content:
        new_id = max([a['id'] for a in articles], default=0) + 1
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        articles.insert(0, {
            "id": new_id,
            "title": title,
            "date": current_date,
            "modified": None,
            "content": content,
            "likes": 0,
            "dislikes": 0
        })
        save_articles(articles)
    
    return redirect(f'/{SECRET_ADMIN_PATH}')

@app.route('/update_article/<int:article_id>', methods=['POST'])
def update_article(article_id):
    title = request.form.get('title')
    content = request.form.get('content')
    
    for art in articles:
        if art['id'] == article_id:
            art['title'] = title
            art['content'] = content
            art['modified'] = datetime.now().strftime("%Y-%m-%d")
            break
            
    save_articles(articles)
    return redirect(f'/{SECRET_ADMIN_PATH}')

@app.route('/delete_article/<int:article_id>')
def delete_article(article_id):
    global articles
    articles = [art for art in articles if art['id'] != article_id]
    save_articles(articles)
    return redirect(f'/{SECRET_ADMIN_PATH}')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
