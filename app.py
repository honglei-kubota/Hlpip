from flask import Flask, render_template_string, request, redirect, url_for, abort
from flask import session, flash          # 追加两个辅助函数
LOGIN_USER = {'username': 'test', 'password': '1234'}   # 演示账号
import time

app = Flask(__name__)
app.secret_key = 'ReplaceMeWithSomethingRandom'   # ← 加这一行
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

# ===== 登录 =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if u == LOGIN_USER['username'] and p == LOGIN_USER['password']:
            session['user'] = u
            return redirect(url_for('home'))
        flash('账号或密码错误')
    return render_template_string(BASE_CSS + '''
        <div class="header"><h1>🔑 登录</h1></div>
        <div class="container card">
            <form method="post">
                <label>用户名</label><input name="username">
                <label>密码</label><input type="password" name="password">
                <button type="submit" class="btn-primary">登录</button>
            </form>
        </div>''')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ===== 首页 =====
@app.route('/')
def home():
    if 'user' not in session:  # ← 新增
        return redirect(url_for('login'))
    return render_template_string(BASE_CSS + '''
    <div class="header">
        <h1>📔 Flask 笔记本</h1>
        {% if session.get('user') %}
        <span style="margin-right:12px;">👤 {{ session.user }}</span>
        <a href="/logout">登出</a>
    {% endif %}
        <a href="/notes">笔记列表</a>
        <a href="/notes/new">+ 新建笔记</a>
        <a href="/qa">问答练习</a>
        <a href="/charts">图表</a>
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

# ========== 问答功能开始 ==========
@app.route('/qa')
def qa_list():
    qa = all_qa()
    return render_template_string(BASE_CSS + '''
        <div class="header">
            <h1>❓ 问答练习</h1>
            <a href="/">首页</a>
            <a href="/notes">笔记</a>
            <a href="/qa/quiz">随机刷题</a>
        </div>
        <div class="container">
        {% for q in qa %}
            <div class="card">
                <h3>{{ q.title }}</h3>
                <details>
                    <summary style="cursor:pointer;color:#4c6ef5;">查看答案</summary>
                    <p style="margin-top:10px;">{{ q.content }}</p>
                </details>
            </div>
        {% endfor %}
        </div>
        ''')

@app.route('/qa/quiz')
def quiz():
    import random
    qa = all_qa()
    if not qa: abort(404)
    q = random.choice(qa)
    return render_template_string(BASE_CSS + '''
        <div class="header">
            <h1>🎯 答题模式</h1>
            <a href="/qa">返回题库</a>
        </div>
        <div class="container">
            <div class="card">
                <h3>{{ q.title }}</h3>
                <details>
                    <summary style="cursor:pointer;color:#4c6ef5;">显示答案</summary>
                    <p style="margin-top:10px;">{{ q.content }}</p>
                </details>
                <br>
                <a class="btn-primary" href="/qa/quiz">下一题</a>
            </div>
        </div>
        ''', q=q)
    # ========== 问答功能结束 ==========

@app.route("/charts")
def charts():
    return render_template_string('''
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>图表</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;
     margin:0;background:#f7f9fc;color:#333;}
.header{background:#4c6ef5;color:#fff;padding:20px 0;text-align:center;}
.header h1{margin:0;font-size:2em;}
.header a{color:#fff;text-decoration:none;background:rgba(255,255,255,.2);
         padding:6px 14px;border-radius:30px;margin:0 6px;}
.container{max-width:800px;margin:30px auto;padding:0 20px;}
.card{background:#fff;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,.08);
      padding:20px;margin-bottom:20px;}
#tagGraph svg{width:100%;height:320px;}
.link{stroke:#999;stroke-opacity:0.6;}
.node{cursor:pointer;}
.node circle{fill:#ff6b6b;stroke:#fa5252;stroke-width:1.5px;}
.node text{font-size:12px;fill:#000;text-anchor:middle;dominant-baseline:middle;}
</style>
</head>
<body>
<div class="header">
    <h1>📊 标签 & 统计图表</h1>
    <a href="/">首页</a>
    <a href="/notes">笔记</a>
</div>
<div class="container">
    <div class="card">
        <h3>📈 最近30天笔记数量</h3>
        <canvas id="lineChart" height="120"></canvas>
    </div>
    <div class="card">
        <h3>🏷️ 标签关联图（D3 力导向）</h3>
        <div id="tagGraph"></div>
    </div>
</div>

<!-- 1. Chart.js 核心（你已有） -->
<script src="{{ url_for('static', filename='js/chart.umd.js') }}"></script>
<!-- 2. D3 v7 力导向图（单文件，无插件冲突） -->
<script src="{{ url_for('static', filename='js/d3.v7.min.js') }}"></script>

<script>
// ===== 折线图（原生 Chart.js） =====
fetch('/api/stats_line')
  .then(r => r.json())
  .then(json => {
      new Chart(document.getElementById('lineChart'), {
          type: 'line',
          data: {
              labels: json.labels,
              datasets: [{
                  label: '新增笔记',
                  data: json.data,
                  borderColor: '#4c6ef5',
                  backgroundColor: 'rgba(76,110,245,.1)',
                  tension: 0.3
              }]
          },
          options: { responsive: true, plugins: { legend: { display: false } } }
      });
  });

// ===== D3 力导向标签关联图 =====
fetch('/api/tag_graph')
  .then(r => r.json())
  .then(json => {
      const width = 540, height = 300;
      const svg = d3.select('#tagGraph')
                    .append('svg')
                    .attr('viewBox', [-width/2, -height/2, width, height]);

      const simulation = d3.forceSimulation(json.nodes)
    .force('link', d3.forceLink(json.links)   // ← 保持默认
          .id(d => d.id)                      // 只告诉它“id 字段叫 id”
          .distance(60))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(0, 0));

      const link = svg.append('g')
          .selectAll('line')
          .data(json.links)
          .join('line')
          .classed('link', true);

      const node = svg.append('g')
          .selectAll('g')
          .data(json.nodes)
          .join('g')
          .classed('node', true)
          .call(d3.drag()
                .on('start', d => { simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
                .on('drag',  d => { d.fx = d3.event.x; d.fy = d3.event.y; })
                .on('end',   d => { d.fx = null; d.fy = null; simulation.alphaTarget(0); }));

      node.append('circle')
          .attr('r', d => 5 + d.size * 1.5);

      node.append('text')
          .text(d => d.label)
          .attr('dy', -8);

      simulation.on('tick', () => {
          link.attr('x1', d => d.source.x)
              .attr('y1', d => d.source.y)
              .attr('x2', d => d.target.x)
              .attr('y2', d => d.target.y);
          node.attr('transform', d => `translate(${d.x},${d.y})`);
      });
});
</script>
</body>
</html>
    ''')

# ========== 图表 JSON 接口（修正版） ==========
from collections import defaultdict
import datetime as dt

@app.route("/api/tag_graph")
def api_tag_graph():
    notes = all_notes()                 # 返回 list[dict]
    tag_cnt = defaultdict(int)
    co_cnt  = defaultdict(int)

    for note in notes:
        # 用中括号取字段
        tags = [t.strip() for t in note["title"].split() if t.startswith("#")]
        for t in tags:
            tag_cnt[t] += 1
        for i, t1 in enumerate(tags):
            for t2 in tags[i+1:]:
                key = frozenset({t1, t2})
                co_cnt[key] += 1

    nodes = [{"id": t, "label": t, "size": c} for t, c in tag_cnt.items()]
    links = [{"source": list(k)[0], "target": list(k)[1], "value": v}
             for k, v in co_cnt.items()]
    return {"nodes": nodes, "links": links}


import datetime as dt

@app.route('/api/stats_line')
def api_stats_line():
    today = dt.date.today()
    days  = [(today - dt.timedelta(d)).strftime("%m-%d") for d in range(29, -1, -1)]
    cnt   = {d: 0 for d in days}

    for idx, note in enumerate(all_notes()):
        raw = note.get("created_at", "")
        key = raw[:10][5:].replace("-0", "-")   # 06-01
        print(f">>> {idx:2d}  raw={raw!r}  key={key!r}  in-window={key in cnt}")
        if key in cnt:
            cnt[key] += 1

    result = {"labels": days, "data": [cnt[d] for d in days]}
    print("=== 最终计数 ===", result)   # ★ 看结果
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)