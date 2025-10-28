import sqlite3
DB = "notes.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    with get_conn() as con:
        con.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL);")

def all_notes():          # 返回 list[dict]
    init_db()
    with get_conn() as con:
        rows = con.execute("SELECT id,title,content FROM notes ORDER BY id DESC").fetchall()
    return [{"id": r[0], "title": r[1], "content": r[2]} for r in rows]

def get_note(note_id):    # 返回 dict or None
    with get_conn() as con:
        r = con.execute("SELECT id,title,content FROM notes WHERE id=?", (note_id,)).fetchone()
    return {"id": r[0], "title": r[1], "content": r[2]} if r else None

def add_note(title, content):
    with get_conn() as con:
        cur = con.execute("INSERT INTO notes(title,content) VALUES(?,?)", (title, content))
        return cur.lastrowid

def upd_note(note_id, title, content):
    with get_conn() as con:
        con.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title, content, note_id))

def del_note(note_id):
    with get_conn() as con:
        con.execute("DELETE FROM notes WHERE id=?", (note_id,))