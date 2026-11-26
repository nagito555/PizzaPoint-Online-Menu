import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / "techstore.sqlite3"
ACCESS_PATH = os.getenv("ACCESS_DB", str(BASE_DIR / "TechStore.accdb"))

def access_connection():
    import pyodbc
    drivers = [d for d in pyodbc.drivers() if "Access" in d]
    if not drivers:
        raise RuntimeError("Microsoft Access ODBC driver not found")
    driver = drivers[-1]
    return pyodbc.connect(
        f"DRIVER={{{driver}}};DBQ={ACCESS_PATH};",
        autocommit=False
    )

def sqlite_connection():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def use_access():
    return os.getenv("USE_ACCESS", "0") == "1"

def get_connection():
    if use_access():
        return access_connection()
    return sqlite_connection()

def initialize():
    if use_access():
        conn = access_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE Products (
                    ID COUNTER PRIMARY KEY,
                    Name TEXT(255),
                    Category TEXT(100),
                    Specs MEMO,
                    Price CURRENCY,
                    Stock INTEGER,
                    ImageURL TEXT(255)
                )
            """)
            conn.commit()
        except Exception:
            # Table likely already exists
            conn.rollback()
        cur.execute("SELECT COUNT(*) FROM Products")
        count = cur.fetchone()[0]
        if count == 0:
            seed_access(cur)
            conn.commit()
        conn.close()
    else:
        conn = sqlite_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                specs TEXT,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                image_url TEXT
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO products(name,category,specs,price,stock,image_url) VALUES(?,?,?,?,?,?)",
                seed_data()
            )
        conn.commit()
        conn.close()

def seed_data():
    return [
        ("Маргарита", "Классика", "Томатный соус, моцарелла, свежий базилик", 590, 15, "https://images.unsplash.com/photo-1579751626657-72bc17010498?auto=format&fit=crop&w=800&q=80"),
        ("Пепперони", "Мясная", "Томатный соус, моцарелла, пикантная пепперони", 690, 12, "https://images.unsplash.com/photo-1628840042765-356cda07504e?auto=format&fit=crop&w=800&q=80"),
        ("Четыре сыра", "Сырная", "Моцарелла, дорблю, пармезан, сливочный сыр", 750, 10, "https://images.unsplash.com/photo-1574063382-2b2f3e8f5?auto=format&fit=crop&w=800&q=80"),
        ("Ветчина и грибы", "Мясная", "Ветчина, шампиньоны, моцарелла, томатный соус", 720, 9, "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?auto=format&fit=crop&w=800&q=80"),
    ]

def seed_access(cur):
    for row in seed_data():
        cur.execute(
            "INSERT INTO Products (Name, Category, Specs, Price, Stock, ImageURL) VALUES (?, ?, ?, ?, ?, ?)",
            row
        )

def query_all(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def execute(sql, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

def table_name():
    return "Products" if use_access() else "products"

def column_names():
    return ("ID", "Name", "Category", "Specs", "Price", "Stock", "ImageURL") if use_access() else ("id", "name", "category", "specs", "price", "stock", "image_url")

def products():
    t = table_name()
    c = column_names()
    return query_all(f"SELECT {', '.join(c)} FROM {t} ORDER BY {c[0]} DESC")

def product_by_id(pid):
    t = table_name(); c = column_names()
    rows = query_all(f"SELECT {', '.join(c)} FROM {t} WHERE {c[0]}=?", (pid,))
    return rows[0] if rows else None

def categories():
    t=table_name(); c=column_names()
    rows=query_all(f"SELECT DISTINCT {c[2]} FROM {t} ORDER BY {c[2]}")
    return [r[0] for r in rows]

def stats():
    t=table_name(); c=column_names()
    total=query_all(f"SELECT COUNT(*) FROM {t}")[0][0]
    category_count=query_all(f"SELECT COUNT(DISTINCT {c[2]}) FROM {t}")[0][0]
    value=query_all(f"SELECT SUM({c[4]} * {c[5]}) FROM {t}")[0][0] or 0
    return total, category_count, value
