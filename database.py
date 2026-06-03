import sqlite3
import os
import pandas as pd
from utils import safe_parse_date, get_image_path

DB_NAME = 'store.db'

def init_db():
    """Создаёт таблицы и импортирует данные из Excel, если БД пуста."""
    if os.path.exists(DB_NAME):
        # Проверим, есть ли данные
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='products'")
        if cur.fetchone()[0] > 0:
            conn.close()
            return
        conn.close()
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Таблица пользователей
    cur.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'client'))
        )
    ''')
    
    # Таблица товаров (артикул - первичный ключ)
    cur.execute('''
        CREATE TABLE products (
            article TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            unit TEXT,
            price REAL NOT NULL,
            supplier TEXT,
            manufacturer TEXT,
            category TEXT,
            discount INTEGER DEFAULT 0,
            stock INTEGER DEFAULT 0,
            description TEXT,
            photo TEXT
        )
    ''')
    
    # Таблица пунктов выдачи
    cur.execute('''
        CREATE TABLE pickup_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Таблица заказов
    cur.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number INTEGER UNIQUE,    -- внешний номер из файла
            order_date DATE,
            delivery_date DATE,
            pickup_address TEXT,
            customer_fio TEXT,
            pickup_code TEXT,
            status TEXT
        )
    ''')
    
    # Таблица составов заказов
    cur.execute('''
        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_article TEXT,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_article) REFERENCES products(article)
        )
    ''')
    
    conn.commit()
    
    # Импорт данных
    import_users_from_excel(conn)
    import_products_from_excel(conn)
    import_pickup_points_from_excel(conn)
    import_orders_from_excel(conn)
    
    conn.close()

def import_users_from_excel(conn):
    file_path = 'user_import.xlsx'
    if not os.path.exists(file_path):
        return
    df = pd.read_excel(file_path)
    # Ожидаемые столбцы: Роль сотрудника, ФИО, Логин, Пароль
    role_map = {'Администратор': 'admin', 'Менеджер': 'manager', 'Авторизированный клиент': 'client'}
    cur = conn.cursor()
    for _, row in df.iterrows():
        role = role_map.get(row['Роль сотрудника'], 'client')
        full_name = row['ФИО']
        login = row['Логин']
        password = row['Пароль']
        try:
            cur.execute("INSERT INTO users (full_name, login, password, role) VALUES (?,?,?,?)",
                        (full_name, login, password, role))
        except sqlite3.IntegrityError:
            pass  # логин уже существует
    conn.commit()

def import_products_from_excel(conn):
    file_path = 'Tovar.xlsx'
    if not os.path.exists(file_path):
        return
    df = pd.read_excel(file_path)
    cur = conn.cursor()
    for _, row in df.iterrows():
        article = str(row['Артикул']).strip()
        name = row['Наименование товара']
        unit = row.get('Единица измерения', 'шт')
        price = float(row['Цена'])
        supplier = row.get('Поставщик', '')
        manufacturer = row.get('Производитель', '')
        category = row.get('Категория товара', '')
        discount = int(row.get('Действующая скидка', 0))
        stock = int(row.get('Кол-во на складе', 0))
        description = row.get('Описание товара', '')
        photo = row.get('Фото', '')
        cur.execute('''
            INSERT OR REPLACE INTO products 
            (article, name, unit, price, supplier, manufacturer, category, discount, stock, description, photo)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        ''', (article, name, unit, price, supplier, manufacturer, category, discount, stock, description, photo))
    conn.commit()

def import_pickup_points_from_excel(conn):
    file_path = 'Пункты выдачи_import.xlsx'
    if not os.path.exists(file_path):
        return
    df = pd.read_excel(file_path, header=None)
    cur = conn.cursor()
    for _, row in df.iterrows():
        address = str(row[0]).strip()
        cur.execute("INSERT OR IGNORE INTO pickup_points (address) VALUES (?)", (address,))
    conn.commit()

def import_orders_from_excel(conn):
    file_path = 'Заказ_import.xlsx'
    if not os.path.exists(file_path):
        return
    df = pd.read_excel(file_path)
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        order_number = int(row['Номер заказа'])
        # Парсинг состава заказа: строка вида "PMEZMH, 2, BPV4MM, 2"
        items_str = str(row['Артикул заказа'])
        items_parts = [x.strip() for x in items_str.split(',')]
        items = []
        for i in range(0, len(items_parts), 2):
            if i+1 < len(items_parts):
                art = items_parts[i]
                try:
                    qty = int(items_parts[i+1])
                    items.append((art, qty))
                except:
                    pass
        
        order_date = safe_parse_date(row['Дата заказа'])
        delivery_date = safe_parse_date(row['Дата доставки'])
        pickup_address = str(row['Адрес пункта выдачи']).strip()
        customer_fio = row['ФИО авторизированного клиента']
        pickup_code = str(row['Код для получения']).strip()
        status = row['Статус заказа']
        
        # Вставляем заказ
        cur.execute('''
            INSERT INTO orders (order_number, order_date, delivery_date, pickup_address, customer_fio, pickup_code, status)
            VALUES (?,?,?,?,?,?,?)
        ''', (order_number, order_date, delivery_date, pickup_address, customer_fio, pickup_code, status))
        order_id = cur.lastrowid
        
        # Вставляем позиции
        for art, qty in items:
            cur.execute('''
                INSERT INTO order_items (order_id, product_article, quantity)
                VALUES (?,?,?)
            ''', (order_id, art, qty))
    conn.commit()

# --- Функции CRUD для приложения ---

def authenticate(login, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT role, full_name FROM users WHERE login=? AND password=?', (login, password))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return None, None

def get_all_products():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT article, name, price, discount, stock, description, category, photo FROM products')
    rows = cur.fetchall()
    conn.close()
    return rows

def add_product(article, name, price, discount, stock, description, category, unit, supplier, manufacturer, photo):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO products (article, name, price, discount, stock, description, category, unit, supplier, manufacturer, photo)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    ''', (article, name, price, discount, stock, description, category, unit, supplier, manufacturer, photo))
    conn.commit()
    conn.close()

def update_product(article, name, price, discount, stock, description, category, unit, supplier, manufacturer, photo):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        UPDATE products SET name=?, price=?, discount=?, stock=?, description=?, category=?, unit=?, supplier=?, manufacturer=?, photo=?
        WHERE article=?
    ''', (name, price, discount, stock, description, category, unit, supplier, manufacturer, photo, article))
    conn.commit()
    conn.close()

def delete_product(article):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM products WHERE article=?', (article,))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT id, order_number, order_date, customer_fio, status, pickup_address FROM orders ORDER BY order_date DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

def get_order_items(order_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        SELECT oi.product_article, p.name, oi.quantity, p.price, p.discount
        FROM order_items oi
        JOIN products p ON oi.product_article = p.article
        WHERE oi.order_id=?
    ''', (order_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def add_order(order_number, order_date, delivery_date, pickup_address, customer_fio, pickup_code, status, items):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO orders (order_number, order_date, delivery_date, pickup_address, customer_fio, pickup_code, status)
        VALUES (?,?,?,?,?,?,?)
    ''', (order_number, order_date, delivery_date, pickup_address, customer_fio, pickup_code, status))
    order_id = cur.lastrowid
    for art, qty in items:
        cur.execute('INSERT INTO order_items (order_id, product_article, quantity) VALUES (?,?,?)', (order_id, art, qty))
    conn.commit()
    conn.close()
    return order_id

def update_order(order_id, order_number, order_date, delivery_date, pickup_address, customer_fio, pickup_code, status, items):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        UPDATE orders SET order_number=?, order_date=?, delivery_date=?, pickup_address=?, customer_fio=?, pickup_code=?, status=?
        WHERE id=?
    ''', (order_number, order_date, delivery_date, pickup_address, customer_fio, pickup_code, status, order_id))
    # Удалить старые позиции и вставить новые
    cur.execute('DELETE FROM order_items WHERE order_id=?', (order_id,))
    for art, qty in items:
        cur.execute('INSERT INTO order_items (order_id, product_article, quantity) VALUES (?,?,?)', (order_id, art, qty))
    conn.commit()
    conn.close()

def delete_order(order_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM order_items WHERE order_id=?', (order_id,))
    cur.execute('DELETE FROM orders WHERE id=?', (order_id,))
    conn.commit()
    conn.close()

def get_pickup_points():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT address FROM pickup_points ORDER BY address')
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]