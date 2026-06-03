import tkinter as tk
from tkinter import ttk, messagebox
import database as db
from main_window import MainWindow

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Мир Игрушек - Вход")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.configure(bg='#FFFFFF')
        self.set_style()
        self.create_widgets()
        self.root.mainloop()

    def set_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#FFFFFF', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), background='#DEB887')
        style.map('TButton', background=[('active', '#DEB887')])
        style.configure('TEntry', font=('Arial', 10))

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_login = ttk.Entry(frame, width=25)
        self.entry_login.grid(row=0, column=1, pady=5)
        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_pass = ttk.Entry(frame, width=25, show="*")
        self.entry_pass.grid(row=1, column=1, pady=5)
        btn_login = ttk.Button(frame, text="Войти", command=self.do_login)
        btn_login.grid(row=2, column=0, columnspan=2, pady=10)
        btn_guest = ttk.Button(frame, text="Войти как гость", command=self.guest_login)
        btn_guest.grid(row=3, column=0, columnspan=2, pady=5)

    def do_login(self):
        login = self.entry_login.get().strip()
        pwd = self.entry_pass.get().strip()
        if not login or not pwd:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return
        role, full_name = db.authenticate(login, pwd)
        if role:
            self.root.destroy()
            MainWindow(role, full_name)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def guest_login(self):
        self.root.destroy()
        MainWindow('guest', 'Гость')