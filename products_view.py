import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import database as db
from add_edit_dialog import AddEditProductDialog
from utils import get_image_path

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import database as db
from add_edit_dialog import AddEditProductDialog
from utils import get_image_path

class ProductsView:
    def __init__(self, parent, role):
        self.parent = parent
        self.role = role
        self.current_filter = ""
        self.create_widgets()
        self.load_products()

    def create_widgets(self):
        # Панель фильтрации (только manager/admin)
        self.filter_frame = ttk.Frame(self.parent)
        self.filter_frame.pack(fill='x', padx=5, pady=5)
        if self.role in ('manager', 'admin'):
            ttk.Label(self.filter_frame, text="Поиск:").pack(side='left', padx=5)
            self.search_var = tk.StringVar()
            self.search_entry = ttk.Entry(self.filter_frame, textvariable=self.search_var, width=20)
            self.search_entry.pack(side='left', padx=5)
            self.search_entry.bind('<KeyRelease>', self.on_search)
            ttk.Label(self.filter_frame, text="Сортировка:").pack(side='left', padx=5)
            self.sort_var = tk.StringVar(value="name")
            sort_combo = ttk.Combobox(self.filter_frame, textvariable=self.sort_var, values=["name", "price"], state='readonly', width=10)
            sort_combo.pack(side='left', padx=5)
            sort_combo.bind('<<ComboboxSelected>>', self.on_sort)
            ttk.Label(self.filter_frame, text="Порядок:").pack(side='left', padx=5)
            self.order_var = tk.StringVar(value="ASC")
            order_combo = ttk.Combobox(self.filter_frame, textvariable=self.order_var, values=["ASC", "DESC"], state='readonly', width=6)
            order_combo.pack(side='left', padx=5)
            order_combo.bind('<<ComboboxSelected>>', self.on_sort)
            ttk.Button(self.filter_frame, text="Сброс", command=self.reset_filters).pack(side='left', padx=10)
        # Кнопка добавления (admin)
        if self.role == 'admin':
            ttk.Button(self.filter_frame, text="Добавить товар", command=self.add_product).pack(side='right', padx=5)
        
        # Таблица товаров
        columns = ('article', 'name', 'price', 'discount', 'stock', 'category')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=15)
        self.tree.heading('article', text='Артикул')
        self.tree.heading('name', text='Название')
        self.tree.heading('price', text='Цена')
        self.tree.heading('discount', text='Скидка %')
        self.tree.heading('stock', text='Остаток')
        self.tree.heading('category', text='Категория')
        self.tree.column('article', width=100)
        self.tree.column('name', width=250)
        self.tree.column('price', width=80)
        self.tree.column('discount', width=80)
        self.tree.column('stock', width=80)
        self.tree.column('category', width=120)
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Контекстное меню для admin
        if self.role == 'admin':
            self.tree.bind('<Button-3>', self.show_context_menu)
            self.context_menu = tk.Menu(self.parent, tearoff=0)
            self.context_menu.add_command(label="Редактировать", command=self.edit_product)
            self.context_menu.add_command(label="Удалить", command=self.delete_product)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.parent, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_products(self, search_text="", sort_by="name", order="ASC"):
        products = db.get_all_products()
        # Фильтрация
        if search_text:
            products = [p for p in products if search_text.lower() in p[1].lower()]
        # Сортировка
        if sort_by == 'name':
            products.sort(key=lambda x: x[1], reverse=(order == 'DESC'))
        elif sort_by == 'price':
            products.sort(key=lambda x: x[2], reverse=(order == 'DESC'))
        # Очистка
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Вставка с цветовой индикацией скидки >17%
        for prod in products:
            article, name, price, discount, stock, desc, category, photo = prod
            if discount > 17:
                tag = 'high_discount'
                self.tree.tag_configure('high_discount', background='#FFDEAD')
            else:
                tag = ''
            self.tree.insert('', 'end', values=(article, name, price, discount, stock, category), tags=(tag,))

    def on_search(self, event):
        self.load_products(self.search_var.get(), self.sort_var.get(), self.order_var.get())

    def on_sort(self, event):
        self.load_products(self.search_var.get(), self.sort_var.get(), self.order_var.get())

    def reset_filters(self):
        self.search_var.set("")
        self.sort_var.set("name")
        self.order_var.set("ASC")
        self.load_products()

    def add_product(self):
        dialog = AddEditProductDialog(self.parent, title="Добавление товара")
        if dialog.result:
            db.add_product(*dialog.result)
            self.load_products()

    def edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар")
            return
        item = self.tree.item(selected[0])['values']
        article = item[0]
        # Получим полные данные товара
        conn = sqlite3.connect(db.DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE article=?", (article,))
        prod = cur.fetchone()
        conn.close()
        dialog = AddEditProductDialog(self.parent, title="Редактирование товара", product=prod)
        if dialog.result:
            db.update_product(article, *dialog.result)
            self.load_products()

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар")
            return
        if messagebox.askyesno("Подтверждение", "Удалить товар?"):
            article = self.tree.item(selected[0])['values'][0]
            db.delete_product(article)
            self.load_products()

    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)