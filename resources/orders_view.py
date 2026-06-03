import tkinter as tk
from tkinter import ttk, messagebox
import database as db
from add_edit_dialog import AddEditOrderDialog

class OrdersView:
    def __init__(self, parent, role):
        self.parent = parent
        self.role = role
        self.create_widgets()
        self.load_orders()

    def create_widgets(self):
        top_frame = ttk.Frame(self.parent)
        top_frame.pack(fill='x', padx=5, pady=5)
        if self.role == 'admin':
            ttk.Button(top_frame, text="Добавить заказ", command=self.add_order).pack(side='left', padx=5)
        
        columns = ('id', 'order_number', 'order_date', 'customer_fio', 'status', 'pickup_address')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.heading('order_number', text='№ заказа')
        self.tree.heading('order_date', text='Дата')
        self.tree.heading('customer_fio', text='Клиент')
        self.tree.heading('status', text='Статус')
        self.tree.heading('pickup_address', text='Пункт выдачи')
        self.tree.column('id', width=40)
        self.tree.column('order_number', width=80)
        self.tree.column('order_date', width=100)
        self.tree.column('customer_fio', width=200)
        self.tree.column('status', width=100)
        self.tree.column('pickup_address', width=300)
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        if self.role == 'admin':
            self.tree.bind('<Button-3>', self.show_context_menu)
            self.context_menu = tk.Menu(self.parent, tearoff=0)
            self.context_menu.add_command(label="Редактировать", command=self.edit_order)
            self.context_menu.add_command(label="Удалить", command=self.delete_order)
        
        scrollbar = ttk.Scrollbar(self.parent, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Двойной клик для просмотра состава
        self.tree.bind('<Double-1>', self.view_order_details)

    def load_orders(self):
        orders = db.get_all_orders()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for order in orders:
            self.tree.insert('', 'end', values=order)

    def view_order_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        order_id = self.tree.item(selected[0])['values'][0]
        items = db.get_order_items(order_id)
        if not items:
            messagebox.showinfo("Состав заказа", "Нет позиций")
            return
        details = "\n".join([f"{art} - {name}: {qty} шт." for art, name, qty, _, _ in items])
        messagebox.showinfo(f"Заказ №{order_id}", details)

    def add_order(self):
        dialog = AddEditOrderDialog(self.parent, title="Добавление заказа")
        if dialog.result:
            db.add_order(*dialog.result)
            self.load_orders()

    def edit_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        order_id = self.tree.item(selected[0])['values'][0]
        # Получим полные данные
        conn = sqlite3.connect(db.DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        order = cur.fetchone()
        cur.execute("SELECT product_article, quantity FROM order_items WHERE order_id=?", (order_id,))
        items = cur.fetchall()
        conn.close()
        dialog = AddEditOrderDialog(self.parent, title="Редактирование заказа", order=order, items=items)
        if dialog.result:
            db.update_order(order_id, *dialog.result)
            self.load_orders()

    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        if messagebox.askyesno("Подтверждение", "Удалить заказ?"):
            order_id = self.tree.item(selected[0])['values'][0]
            db.delete_order(order_id)
            self.load_orders()

    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)