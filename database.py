"""PizzaPoint database layer.

SQLite is the default database. The menu uses a relational structure:
Categories(id) <- Products(category_id). Queries that display category names
use JOIN and are commented to explain the relationship.
"""
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / "pizzapoint.sqlite3"
ACCESS_PATH = os.getenv("ACCESS_DB", str(BASE_DIR / "PizzaPoint.accdb"))


def sqlite_connection():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    # Enable enforcement of foreign-key relationships on every connection.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def use_access():
    # Optional Access mode. SQLite is the recommended mode for this project.
    return os.getenv("USE_ACCESS", "0") == "1"


def access_connection():
    import pyodbc
    drivers = [d for d in pyodbc.drivers() if "Access" in d]
    if not drivers:
        raise RuntimeError("Microsoft Access ODBC driver not found")
    return pyodbc.connect(f"DRIVER={{{drivers[-1]}}};DBQ={ACCESS_PATH};", autocommit=False)


def get_connection():
    return access_connection() if use_access() else sqlite_connection()


def seed_data():
    return [
        ("Маргарита", "Классика", "Томатный соус, моцарелла, свежий базилик", 590, 15, "https://images.unsplash.com/photo-1579751626657-72bc17010498?auto=format&fit=crop&w=800&q=80"),
        ("Пепперони", "Мясная", "Томатный соус, моцарелла, пикантная пепперони", 690, 12, "https://images.unsplash.com/photo-1628840042765-356cda07504e?auto=format&fit=crop&w=800&q=80"),
        ("Четыре сыра", "Сырная", "Моцарелла, дорблю, пармезан, сливочный сыр", 750, 10, "https://images.unsplash.com/photo-1574063382-2b2f3e8f5?auto=format&fit=crop&w=800&q=80"),
        ("Ветчина и грибы", "Мясная", "Ветчина, шампиньоны, моцарелла, томатный соус", 720, 9, "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?auto=format&fit=crop&w=800&q=80"),
    ]


def initialize():
    conn = sqlite_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            specs TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            image_url TEXT,
            FOREIGN KEY(category_id) REFERENCES categories(id)
                ON UPDATE CASCADE ON DELETE RESTRICT
        );
    """)
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        for name, category, specs, price, stock, image in seed_data():
            category_id = ensure_category(conn, category)
            conn.execute("INSERT INTO products(name,category_id,specs,price,stock,image_url) VALUES(?,?,?,?,?,?)",
                         (name, category_id, specs, price, stock, image))
    conn.commit()
    conn.close()


def ensure_category(conn, category_name):
    conn.execute("INSERT OR IGNORE INTO categories(name) VALUES(?)", (category_name,))
    return conn.execute("SELECT id FROM categories WHERE name=?", (category_name,)).fetchone()[0]


def products():
    conn = sqlite_connection()
    # JOIN retrieves the category name via Products.category_id -> Categories.id.
    rows = conn.execute("""
        SELECT p.id, p.name, c.name AS category, p.specs, p.price, p.stock, p.image_url
        FROM products AS p
        INNER JOIN categories AS c ON p.category_id = c.id
        ORDER BY p.id DESC
    """).fetchall()
    conn.close()
    return rows


def product_by_id(pid):
    conn = sqlite_connection()
    # JOIN follows the same foreign-key relationship for one selected product.
    row = conn.execute("""
        SELECT p.id, p.name, c.name AS category, p.specs, p.price, p.stock, p.image_url
        FROM products AS p
        INNER JOIN categories AS c ON p.category_id = c.id
        WHERE p.id = ?
    """, (pid,)).fetchone()
    conn.close()
    return row


def categories():
    conn = sqlite_connection()
    rows = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
    conn.close()
    return [row[0] for row in rows]


def stats():
    conn = sqlite_connection()
    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    category_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    value = conn.execute("SELECT COALESCE(SUM(price * stock),0) FROM products").fetchone()[0]
    conn.close()
    return total, category_count, value


def add_product(name, category, specs, price, stock, image_url):
    conn = sqlite_connection()
    category_id = ensure_category(conn, category)
    conn.execute("INSERT INTO products(name,category_id,specs,price,stock,image_url) VALUES(?,?,?,?,?,?)",
                 (name, category_id, specs, price, stock, image_url))
    conn.commit(); conn.close()


def update_product(pid, name, category, specs, price, stock, image_url):
    conn = sqlite_connection()
    category_id = ensure_category(conn, category)
    conn.execute("UPDATE products SET name=?,category_id=?,specs=?,price=?,stock=?,image_url=? WHERE id=?",
                 (name, category_id, specs, price, stock, image_url, pid))
    conn.commit(); conn.close()


def delete_product(pid):
    conn = sqlite_connection()
    conn.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit(); conn.close()
