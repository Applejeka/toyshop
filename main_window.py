import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from products_view import ProductsView
from orders_view import OrdersView

class MainWindow:
    def __init__(self, role, username):
        self.role = role
        self.username = username
        self.root = tk.Tk()
        self.root.title("Мир Игрушек - Главная")
        self.root.geometry("1100x650")
        self.root.configure(bg='#FFFFFF')
        self.set_icon()
        self.set_style()
        self.create_header()
        self.create_notebook()
        self.root.mainloop()

    def set_icon(self):
        try:
            icon_path = os.path.join('resources', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass

    def set_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#FFFFFF')
        style.configure('TNotebook.Tab', font=('Arial', 10), background='#F5DEB3')
        style.configure('TFrame', background='#FFFFFF')
        style.configure('TLabel', background='#FFFFFF', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), background='#DEB887')
        style.map('TButton', background=[('active', '#DEB887')])

    def create_header(self):
        header = ttk.Frame(self.root, height=100)
        header.pack(fill='x', padx=10, pady=5)
        # Логотип
        logo_path = os.path.join('resources', 'logo.png')
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((100, 80), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = ttk.Label(header, image=logo_img)
            logo_label.image = logo_img
            logo_label.pack(side='left', padx=10)
        else:
            ttk.Label(header, text="ЛОГОТИП", font=('Arial', 16, 'bold')).pack(side='left', padx=10)
        # Приветствие
        ttk.Label(header, text=f"Добро пожаловать, {self.username}!", font=('Arial', 12)).pack(side='left', padx=20)
        # Кнопка выхода
        ttk.Button(header, text="Выход", command=self.logout).pack(side='right', padx=10)

    def create_notebook(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        # Вкладка товаров
        products_tab = ttk.Frame(notebook)
        notebook.add(products_tab, text="Товары")
        self.products_view = ProductsView(products_tab, self.role)
        # Вкладка заказов для менеджера и админа
        if self.role in ('manager', 'admin'):
            orders_tab = ttk.Frame(notebook)
            notebook.add(orders_tab, text="Заказы")
            self.orders_view = OrdersView(orders_tab, self.role)

    def logout(self):
        self.root.destroy()
        from login_window import LoginWindow
        LoginWindow()