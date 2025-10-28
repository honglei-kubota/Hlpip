from flask import Flask, render_template_string, request, redirect, url_for, abort
import time

app = Flask(__name__)

# 内存数据库：id 自增
NOTES = {
    1: {"title": "测试笔记1", "content": "这是第一条测试数据"},
    2: {"title": "测试笔记2", "content": "这是第二条测试数据"},
}
_next_id = 3

# ===== 通用 CSS =====
BASE_CSS = '''
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;
     margin:0;background:#f7f9fc;color:#333;}
.header{background:#4c6ef5;color:#fff;padding:20px 0;text-align:center;}
.header h1{margin:0;font-size:2em;}
.header a{color:#fff;text-decoration:none;background:rgba(255,255,255,.2);
         padding:6px 14px;border-radius:30px;margin:0 6px;}
.header a:hover{background:rgba(255,255,255,.3);}
.container{max-width:800px;margin:30px auto;padding:0 20px;}
.card{background:#fff;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,.08);
      padding:20px;margin-bottom:20px;}
.btn-primary{background:#4c6ef5;color:#fff;padding:6px 14px;border-radius:4px;text-decoration:none;}
.btn-primary:hover{background:#3b5bdb;}
.btn-warning{background:#fab005;color:#fff;}
.btn-danger{background:#fa5252;color:#fff;}
form input,form textarea{width:100%;padding:8px;margin:6px 0 12px;border:1px solid #ccc;border-radius:4px;}
form textarea{resize:vertical;min-height:120px;}
</style>
'''

# ===== 首页 =====
@app.route('/')
def home():
    return render_template_string(BASE_CSS + '''
    <div class="header">
        <h1>📔 Flask 笔记本</h1>
        <a href="/notes">笔记列表</a>
        <a href="/notes/new">+ 新建笔记</a>
    </div>
    <div class="container">
        <div class="card">
            <h3>🎯 使用提示</h3>
            <p>点击“笔记列表”可查看、编辑、删除已有笔记；点击“+ 新建笔记”可创建。</p>
        </div>
    </div>
    ''')

# ===== 列表页 =====
@app.route('/notes')
def notes():
    return render_template_string(BASE_CSS + '''
    <div class="header">
        <h1>📚 笔记列表</h1>
        <a href="/">首页</a>
        <a href="/notes/new">+ 新建笔记</a>
    </div>
    <div class="container">
        {% for id, note in notes.items() %}
        <div class="card">
            <h3>{{ note.title }}</h3>
            <p>{{ note.content[:80] }}…</p>
            <div>
                <a class="btn-primary" href="/notes/{{ id }}">查看</a>
                <a class="btn-warning" href="/notes/{{ id }}/edit">编辑</a>
                <a class="btn-danger" href="/notes/{{ id }}/delete">删除</a>
            </div>
        </div>
        {% endfor %}
    </div>
    ''', notes=NOTES)

# ===== 创建 =====
@app.route('/notes/new', methods=['GET', 'POST'])
def new_note():
    if request.method == 'POST':
        global _next_id
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            return "标题和内容不能为空！", 400
        NOTES[_next_id] = {"title": title, "content": content}
        _next_id += 1
        return redirect(url_for('notes'))
    # GET
    return render_template_string(BASE_CSS + '''
    <div class="header"><h1>✍️ 新建笔记</h1><a href="/notes">返回列表</a></div>
    <div class="container">
        <form method="post">
            <label>标题</label><input name="title" placeholder="请输入标题">
            <label>内容</label><textarea name="content" placeholder="请输入内容"></textarea>
            <button type="submit" class="btn-primary">保存</button>
        </form>
    </div>
    ''')

# ===== 查看单条 =====
@app.route('/notes/<int:note_id>')
def note_detail(note_id):
    note = NOTES.get(note_id)
    if not note:
        abort(404)
    return render_template_string(BASE_CSS + '''
    <div class="header">
        <h1>{{ note.title }}</h1>
        <a href="/notes">返回列表</a>
        <a href="/notes/{{ note_id }}/edit">编辑</a>
    </div>
    <div class="container">
        <div class="card">
            <p>{{ note.content }}</p>
            <small>创建/编辑时间：{{ ts }}</small>
        </div>
    </div>
    ''', note=note, note_id=note_id, ts=time.strftime("%Y-%m-%d %H:%M:%S"))

# ===== 编辑 =====
@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(note_id):
    note = NOTES.get(note_id)
    if not note:
        abort(404)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            return "标题和内容不能为空！", 400
        note['title'] = title
        note['content'] = content
        return redirect(url_for('note_detail', note_id=note_id))
    # GET
    return render_template_string(BASE_CSS + '''
    <div class="header"><h1>✏️ 编辑笔记</h1><a href="/notes">返回列表</a></div>
    <div class="container">
        <form method="post">
            <label>标题</label><input name="title" value="{{ note.title }}">
            <label>内容</label><textarea name="content">{{ note.content }}</textarea>
            <button type="submit" class="btn-primary">保存修改</button>
        </form>
    </div>
    ''', note=note)

# ===== 删除 =====
@app.route('/notes/<int:note_id>/delete')
def delete_note(note_id):
    if note_id in NOTES:
        del NOTES[note_id]
    return redirect(url_for('notes'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)