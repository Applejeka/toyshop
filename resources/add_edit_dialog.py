import tkinter as tk
from tkinter import ttk, messagebox
import database as db

class AddEditProductDialog:
    def __init__(self, parent, title, product=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x500")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#FFFFFF')
        self.product = product
        self.create_widgets()
        self.dialog.grab_set()
        self.dialog.wait_window()

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill='both', expand=True)
        fields = [
            ("Артикул:", "entry_article"),
            ("Название:", "entry_name"),
            ("Цена:", "entry_price"),
            ("Скидка (%):", "entry_discount"),
            ("Остаток:", "entry_stock"),
            ("Описание:", "entry_desc"),
            ("Категория:", "entry_category"),
            ("Ед. измерения:", "entry_unit"),
            ("Поставщик:", "entry_supplier"),
            ("Производитель:", "entry_manufacturer"),
            ("Фото (имя файла):", "entry_photo")
        ]
        self.widgets = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            entry = ttk.Entry(frame, width=40)
            entry.grid(row=i, column=1, pady=2)
            self.widgets[key] = entry
        if self.product:
            # product: (article, name, unit, price, supplier, manufacturer, category, discount, stock, description, photo)
            self.widgets['entry_article'].insert(0, self.product[0])
            self.widgets['entry_name'].insert(0, self.product[1])
            self.widgets['entry_price'].insert(0, self.product[3])
            self.widgets['entry_discount'].insert(0, self.product[7])
            self.widgets['entry_stock'].insert(0, self.product[8])
            self.widgets['entry_desc'].insert(0, self.product[9] or '')
            self.widgets['entry_category'].insert(0, self.product[6] or '')
            self.widgets['entry_unit'].insert(0, self.product[2] or '')
            self.widgets['entry_supplier'].insert(0, self.product[4] or '')
            self.widgets['entry_manufacturer'].insert(0, self.product[5] or '')
            self.widgets['entry_photo'].insert(0, self.product[10] or '')
            # Если редактирование, артикул нельзя менять
            self.widgets['entry_article'].config(state='readonly')
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.dialog.destroy).pack(side='left', padx=10)

    def save(self):
        try:
            article = self.widgets['entry_article'].get().strip()
            name = self.widgets['entry_name'].get().strip()
            price = float(self.widgets['entry_price'].get().strip())
            discount = int(self.widgets['entry_discount'].get().strip())
            stock = int(self.widgets['entry_stock'].get().strip())
            description = self.widgets['entry_desc'].get().strip()
            category = self.widgets['entry_category'].get().strip()
            unit = self.widgets['entry_unit'].get().strip()
            supplier = self.widgets['entry_supplier'].get().strip()
            manufacturer = self.widgets['entry_manufacturer'].get().strip()
            photo = self.widgets['entry_photo'].get().strip()
            if not article or not name:
                raise ValueError("Артикул и название обязательны")
            self.result = (article, name, price, discount, stock, description, category, unit, supplier, manufacturer, photo)
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

class AddEditOrderDialog:
    def __init__(self, parent, title, order=None, items=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.configure(bg='#FFFFFF')
        self.order = order
        self.items = items if items else []
        self.create_widgets()
        self.dialog.grab_set()
        self.dialog.wait_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill='both', expand=True)
        # Поля заказа
        fields_frame = ttk.LabelFrame(main_frame, text="Данные заказа", padding="5")
        fields_frame.pack(fill='x', pady=5)
        ttk.Label(fields_frame, text="Номер заказа:").grid(row=0, column=0, sticky='w')
        self.entry_num = ttk.Entry(fields_frame, width=15)
        self.entry_num.grid(row=0, column=1, padx=5)
        ttk.Label(fields_frame, text="Дата заказа (ГГГГ-ММ-ДД):").grid(row=1, column=0, sticky='w')
        self.entry_date = ttk.Entry(fields_frame, width=15)
        self.entry_date.grid(row=1, column=1, padx=5)
        ttk.Label(fields_frame, text="Дата доставки:").grid(row=2, column=0, sticky='w')
        self.entry_delivery = ttk.Entry(fields_frame, width=15)
        self.entry_delivery.grid(row=2, column=1, padx=5)
        ttk.Label(fields_frame, text="Клиент (ФИО):").grid(row=3, column=0, sticky='w')
        self.entry_customer = ttk.Entry(fields_frame, width=30)
        self.entry_customer.grid(row=3, column=1, padx=5)
        ttk.Label(fields_frame, text="Код получения:").grid(row=4, column=0, sticky='w')
        self.entry_code = ttk.Entry(fields_frame, width=15)
        self.entry_code.grid(row=4, column=1, padx=5)
        ttk.Label(fields_frame, text="Статус:").grid(row=5, column=0, sticky='w')
        self.combo_status = ttk.Combobox(fields_frame, values=["Новый", "В обработке", "Доставлен", "Отменён"], state='readonly', width=20)
        self.combo_status.grid(row=5, column=1, padx=5)
        ttk.Label(fields_frame, text="Пункт выдачи:").grid(row=6, column=0, sticky='w')
        points = db.get_pickup_points()
        self.combo_point = ttk.Combobox(fields_frame, values=points, width=40)
        self.combo_point.grid(row=6, column=1, padx=5)
        
        # Блок товаров
        items_frame = ttk.LabelFrame(main_frame, text="Товары в заказе", padding="5")
        items_frame.pack(fill='both', expand=True, pady=5)
        self.items_listbox = tk.Listbox(items_frame, height=8)
        self.items_listbox.pack(fill='both', expand=True, side='left')
        scroll = ttk.Scrollbar(items_frame, orient='vertical', command=self.items_listbox.yview)
        scroll.pack(side='right', fill='y')
        self.items_listbox.configure(yscrollcommand=scroll.set)
        
        btn_frame = ttk.Frame(items_frame)
        btn_frame.pack(side='bottom', fill='x', pady=5)
        ttk.Button(btn_frame, text="Добавить товар", command=self.add_item).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Удалить выбранный", command=self.remove_item).pack(side='left', padx=2)
        
        if self.order:
            # Заполняем данными существующего заказа
            self.entry_num.insert(0, self.order[1])  # order_number
            self.entry_date.insert(0, self.order[2] or '')
            self.entry_delivery.insert(0, self.order[3] or '')
            self.entry_customer.insert(0, self.order[4])
            self.entry_code.insert(0, self.order[6])
            self.combo_status.set(self.order[7])
            self.combo_point.set(self.order[5])
            for item in self.items:
                art, qty = item
                self.items_listbox.insert('end', f"{art} : {qty} шт.")
        
        save_btn = ttk.Button(main_frame, text="Сохранить заказ", command=self.save)
        save_btn.pack(pady=10)

    def add_item(self):
        # Простой диалог для добавления товара
        win = tk.Toplevel(self.dialog)
        win.title("Добавить товар")
        win.geometry("300x150")
        ttk.Label(win, text="Артикул:").pack(pady=5)
        entry_art = ttk.Entry(win)
        entry_art.pack()
        ttk.Label(win, text="Количество:").pack(pady=5)
        entry_qty = ttk.Entry(win)
        entry_qty.pack()
        def add():
            art = entry_art.get().strip()
            try:
                qty = int(entry_qty.get().strip())
                if art and qty > 0:
                    self.items_listbox.insert('end', f"{art} : {qty} шт.")
                    win.destroy()
                else:
                    messagebox.showerror("Ошибка", "Введите корректные данные")
            except:
                messagebox.showerror("Ошибка", "Количество должно быть числом")
        ttk.Button(win, text="OK", command=add).pack(pady=10)

    def remove_item(self):
        selected = self.items_listbox.curselection()
        if selected:
            self.items_listbox.delete(selected[0])

    def save(self):
        try:
            order_num = int(self.entry_num.get().strip())
            order_date = self.entry_date.get().strip() or None
            delivery_date = self.entry_delivery.get().strip() or None
            customer = self.entry_customer.get().strip()
            code = self.entry_code.get().strip()
            status = self.combo_status.get()
            address = self.combo_point.get()
            if not customer or not status or not address:
                raise ValueError("Заполните обязательные поля")
            # Парсим товары
            items = []
            for i in range(self.items_listbox.size()):
                line = self.items_listbox.get(i)
                parts = line.split(':')
                art = parts[0].strip()
                qty = int(parts[1].replace('шт.', '').strip())
                items.append((art, qty))
            if not items:
                raise ValueError("Добавьте хотя бы один товар")
            self.result = (order_num, order_date, delivery_date, address, customer, code, status, items)
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))