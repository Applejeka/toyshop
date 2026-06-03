import database as db
from login_window import LoginWindow

if __name__ == "__main__":
    db.init_db()   # Создаёт БД и импортирует данные из Excel
    LoginWindow()