import sqlite3
DB = "notes.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    with get_conn() as con:
        con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL);")

def all_notes():
    with get_conn() as conn:
        conn.row_factory = sqlite3.Row          # 让行像 dict
        cur = conn.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]

def get_note(note_id):    # 返回 dict or None
    with get_conn() as con:
        r = con.execute("SELECT id,title,content FROM notes WHERE id=?", (note_id,)).fetchone()
    return {"id": r[0], "title": r[1], "content": r[2]} if r else None

def add_note(title, content, _type='note'):
    with get_conn() as con:
        cur = con.execute(
            "INSERT INTO notes(title,content,type, created_at) VALUES(?,?,?,datetime('now','localtime'))",
            (title, content, _type)
        )
        return cur.lastrowid

def upd_note(note_id, title, content):
    with get_conn() as con:
        con.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title, content, note_id))

def del_note(note_id):
    with get_conn() as con:
        con.execute("DELETE FROM notes WHERE id=?", (note_id,))

# 1. 只读问答
def all_qa():
    with get_conn() as con:
        rows = con.execute(
            "SELECT id,title,content FROM notes WHERE type='qa' ORDER BY id DESC"
        ).fetchall()
    return [{"id": r[0], "title": r[1], "content": r[2]} for r in rows]

# 2. 一次性灌 5 道测试题
def seed_qa_once():
    # 先看有没有问答记录
    with get_conn() as con:
        exist = con.execute(
            "SELECT 1 FROM notes WHERE type='qa' LIMIT 1"
        ).fetchone()
    if exist:
        return
    test = [
        ("Python 之父？", "Guido van Rossum"),
        ("Flask 依赖的 WSGI 库？", "Werkzeug"),
        ("Flask 反向生成 URL 的函数？", "url_for"),
        ("HTTP 404 含义？", "Not Found"),
        ("Flask 默认端口？", "5000")
    ]
    for q, a in test:
        add_note(q, a, _type='qa')   # 下面 add_note 已支持 _type