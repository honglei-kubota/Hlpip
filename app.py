from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>首页</h1><a href="/notes">笔记列表</a>'

@app.route('/notes')
def notes():
    return '''
    <h2>笔记列表</h2>
    <h3>测试笔记1</h3><p>这是第一条测试数据</p><hr>
    <h3>测试笔记2</h3><p>这是第二条测试数据</p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)