import sqlite3, time
from pathlib import Path
DB_PATH=Path(__file__).resolve().parent/'accounts.sqlite3'
def connect():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def initialize():
    c=connect(); c.executescript('''
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,full_name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,phone TEXT NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'user',verified INTEGER NOT NULL DEFAULT 0,verify_code TEXT,verify_expiry INTEGER,created_at INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS cart(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,product_id INTEGER NOT NULL,quantity INTEGER NOT NULL DEFAULT 1,UNIQUE(user_id,product_id));
    ''')
    from werkzeug.security import generate_password_hash
    email='admin@pizzapoint.local'; password='PizzaAdmin2026!'
    if not c.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone():
        c.execute('INSERT INTO users(full_name,email,phone,password_hash,role,verified,created_at) VALUES(?,?,?,?,?,?,?)',('Администратор PizzaPoint',email,'+70000000000',generate_password_hash(password),'admin',1,int(time.time())))
    c.commit();c.close()
def user_by_id(uid):
    if not uid:return None
    c=connect();r=c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone();c.close();return dict(r) if r else None
def user_by_email(email):
    c=connect();r=c.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone();c.close();return dict(r) if r else None
def create_pending(full_name,email,phone,pwhash,code):
    c=connect();c.execute('DELETE FROM users WHERE email=? AND verified=0',(email,));c.execute('INSERT INTO users(full_name,email,phone,password_hash,role,verified,verify_code,verify_expiry,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(full_name,email,phone,pwhash,'user',0,code,int(time.time())+600,int(time.time())));c.commit();c.close()
def verify(email,code):
    c=connect();r=c.execute('SELECT * FROM users WHERE email=? AND verified=0',(email,)).fetchone();ok=bool(r and r['verify_code']==code and r['verify_expiry']>=int(time.time()))
    if ok:c.execute('UPDATE users SET verified=1,verify_code=NULL,verify_expiry=NULL WHERE id=?',(r['id'],));c.commit()
    c.close();return ok
def cart_raw(uid):
    c=connect();rows=c.execute('SELECT product_id,quantity FROM cart WHERE user_id=?',(uid,)).fetchall();c.close();return [dict(x) for x in rows]
def cart_count(uid):
    c=connect();r=c.execute('SELECT COALESCE(SUM(quantity),0) n FROM cart WHERE user_id=?',(uid,)).fetchone();c.close();return r['n']
def add_cart(uid,pid):
    c=connect();c.execute('INSERT INTO cart(user_id,product_id,quantity) VALUES(?,?,1) ON CONFLICT(user_id,product_id) DO UPDATE SET quantity=quantity+1',(uid,pid));c.commit();c.close()
def set_quantity(uid,pid,q):
    c=connect();c.execute('DELETE FROM cart WHERE user_id=? AND product_id=?',(uid,pid)) if q<=0 else c.execute('UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?',(q,uid,pid));c.commit();c.close()
def remove_cart(uid,pid):
    c=connect();c.execute('DELETE FROM cart WHERE user_id=? AND product_id=?',(uid,pid));c.commit();c.close()
def remove_product(pid):
    c=connect();c.execute('DELETE FROM cart WHERE product_id=?',(pid,));c.commit();c.close()
