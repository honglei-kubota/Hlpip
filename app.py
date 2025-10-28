from flask import Flask, render_template_string, request, redirect, url_for, abort
import time

app = Flask(__name__)
import os
from database import *          # ← 改这里：引入 SQLite 工具
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
.btn-primary, .btn-warning, .btn-danger {
    display: inline-block;
    width: 52px;          /* 统一宽度 */
    height: 28px;         /* 统一高度 */
    line-height: 28px;    /* 文字垂直居中 */
    text-align: center;   /* 文字水平居中 */
    font-size: 14px;      /* 字号一致 */
    padding: 0;           /* 去掉默认内边距 */
    border: none;         /* 去掉边框差异 */
}
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
            <h3>🎯 使用提示-hlhlhl</h3>
            <p>点击“笔记列表”可查看、编辑、删除已有笔记；点击“+ 新建笔记”可创建。</p>
        </div>
    </div>
    ''')

# ===== 列表页 =====
@app.route('/notes')
def notes():
    notes = all_notes()          # ← 改这里：SQLite 查询
    return render_template_string(BASE_CSS + '''
            <div class="header">
                <h1>📚 笔记列表</h1>
                <a href="/">首页</a>
                <a href="/notes/new">+ 新建笔记</a>
            </div>
            <div class="container">
                {% for note in notes %}                      {# ← 这里改 #}
                <div class="card">
                    <h3>{{ note.title }}</h3>
                    <p>{{ note.content[:80] }}…</p>
                    <div>
                        <a class="btn-primary" href="/notes/{{ note.id }}">查看</a>
                        <a class="btn-warning" href="/notes/{{ note.id }}/edit">编辑</a>
                        <a class="btn-danger" href="/notes/{{ note.id }}/delete">删除</a>
                    </div>
                </div>
                {% endfor %}
            </div>
            ''', notes=notes)

# ===== 查看单条 =====
@app.route('/notes/<int:note_id>')
def note_detail(note_id):
    note = get_note(note_id)          # ← 改这里：SQLite 单条查询
    if not note:
        abort(404)
    return render_template_string('''
    <div class="header">
        <h1>{{ note.title }}</h1>
        <a href="/notes">返回列表</a>
        <a href="/notes/{{ note.id }}/edit">编辑</a>
    </div>
    <div class="container">
        <div class="card">
            <p>{{ note.content }}</p>
            <small>创建/编辑时间：{{ ts }}</small>
        </div>
    </div>
    ''', note=note, ts=time.strftime("%Y-%m-%d %H:%M:%S"))

# ===== 创建 =====
@app.route('/notes/new', methods=['GET', 'POST'])
def new_note():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            return "标题和内容不能为空！", 400
        add_note(title, content)          # ← 改这里：SQLite 插入
        return redirect(url_for('notes'))
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

# ===== 编辑 =====
@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(note_id):
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            return "标题和内容不能为空！", 400
        upd_note(note_id, title, content)          # ← 改这里：SQLite 更新
        return redirect(url_for('note_detail', note_id=note_id))
    note = get_note(note_id)                       # ← 改这里：SQLite 读取
    if not note:
        abort(404)
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
    del_note(note_id)          # ← 改这里：SQLite 删除

    return redirect(url_for('notes'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)