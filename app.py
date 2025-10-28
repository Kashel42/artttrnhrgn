# workout_tracker_full.py
import sqlite3
from datetime import datetime
import hashlib

class WorkoutTracker:
    def __init__(self, db_name='gym_app.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.current_trainer = None
        self.create_tables()
        self.add_sample_data()

    def create_tables(self):
        """Создание таблиц в базе данных"""
        # Таблица тренеров
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trainers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL
            )
        ''')

        # Таблица клиентов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                date_of_birth DATE,
                phone TEXT,
                trainer_id INTEGER,
                FOREIGN KEY (trainer_id) REFERENCES trainers (id)
            )
        ''')

        # Таблица тренировок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                date DATE NOT NULL,
                exercise_name TEXT NOT NULL,
                sets INTEGER,
                reps INTEGER,
                weight_kg REAL,
                notes TEXT,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        self.conn.commit()

    def add_sample_data(self):
        """Добавление тестовых данных"""
        try:
            # Проверяем, есть ли уже тренеры
            self.cursor.execute("SELECT COUNT(*) FROM trainers")
            if self.cursor.fetchone()[0] == 0:
                # Добавляем тестового тренера
                password_hash = self.hash_password("1234")
                self.cursor.execute(
                    "INSERT INTO trainers (login, password_hash, full_name) VALUES (?, ?, ?)",
                    ("trainer1", password_hash, "Иванов Алексей")
                )
                self.conn.commit()
                print("Добавлен тестовый тренер: логин - trainer1, пароль - 1234")
        except:
            pass

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_trainer(self, login, password, full_name):
        """Регистрация нового тренера"""
        try:
            if len(login) < 3:
                print("Ошибка: Логин должен содержать минимум 3 символа.")
                return False
            if len(password) < 4:
                print("Ошибка: Пароль должен содержать минимум 4 символа.")
                return False
            
            password_hash = self.hash_password(password)
            self.cursor.execute(
                "INSERT INTO trainers (login, password_hash, full_name) VALUES (?, ?, ?)",
                (login, password_hash, full_name)
            )
            self.conn.commit()
            print(f"Тренер {full_name} успешно зарегистрирован.")
            return True
        except sqlite3.IntegrityError:
            print("Ошибка: Логин уже существует.")
            return False

    def login_trainer(self, login, password):
        """Авторизация тренера"""
        try:
            password_hash = self.hash_password(password)
            self.cursor.execute(
                "SELECT id, full_name FROM trainers WHERE login = ? AND password_hash = ?",
                (login, password_hash)
            )
            result = self.cursor.fetchone()
            if result:
                self.current_trainer = {'id': result[0], 'full_name': result[1]}
                print(f"Добро пожаловать, {result[1]}!")
                return True
            else:
                print("Неверный логин или пароль.")
                return False
        except Exception as e:
            print(f"Ошибка при входе: {e}")
            return False

    def logout(self):
        """Выход из системы"""
        self.current_trainer = None
        print("Вы вышли из системы.")

    def is_authenticated(self):
        return self.current_trainer is not None

    def add_client(self, full_name, date_of_birth, phone=""):
        """Добавление нового клиента"""
        if not self.is_authenticated():
            print("Ошибка: Необходимо авторизоваться.")
            return False

        try:
            self.cursor.execute(
                "INSERT INTO clients (full_name, date_of_birth, phone, trainer_id) VALUES (?, ?, ?, ?)",
                (full_name, date_of_birth, phone, self.current_trainer['id'])
            )
            self.conn.commit()
            print(f"Клиент {full_name} успешно добавлен.")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении клиента: {e}")
            return False

    def get_my_clients(self):
        """Получение списка клиентов текущего тренера"""
        if not self.is_authenticated():
            print("Ошибка: Необходимо авторизоваться.")
            return []

        try:
            self.cursor.execute(
                """SELECT id, full_name, date_of_birth, phone 
                   FROM clients WHERE trainer_id = ? 
                   ORDER BY full_name""",
                (self.current_trainer['id'],)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении списка клиентов: {e}")
            return []

    def search_clients(self, search_term):
        """Поиск клиентов по имени"""
        if not self.is_authenticated():
            print("Ошибка: Необходимо авторизоваться.")
            return []

        try:
            self.cursor.execute(
                """SELECT id, full_name, date_of_birth, phone 
                   FROM clients 
                   WHERE trainer_id = ? AND full_name LIKE ? 
                   ORDER BY full_name""",
                (self.current_trainer['id'], f'%{search_term}%')
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при поиске клиентов: {e}")
            return []

    def add_workout(self, client_id, exercise_name, sets, reps, weight_kg, notes=""):
        """Добавление записи о тренировке"""
        try:
            today = datetime.now().date()
            self.cursor.execute(
                """INSERT INTO workouts (client_id, date, exercise_name, sets, reps, weight_kg, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (client_id, today, exercise_name, sets, reps, weight_kg, notes)
            )
            self.conn.commit()
            print("Запись о тренировке добавлена.")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении тренировки: {e}")
            return False

    def get_client_workouts(self, client_id):
        """Получение тренировок клиента"""
        try:
            self.cursor.execute(
                """SELECT date, exercise_name, sets, reps, weight_kg, notes 
                   FROM workouts WHERE client_id = ? 
                   ORDER BY date DESC""",
                (client_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении тренировок: {e}")
            return []

    def get_client_stats(self, client_id):
        """Получение статистики клиента"""
        try:
            # Общее количество тренировок
            self.cursor.execute(
                "SELECT COUNT(*) FROM workouts WHERE client_id = ?",
                (client_id,)
            )
            total_workouts = self.cursor.fetchone()[0]

            # Последняя тренировка
            self.cursor.execute(
                "SELECT date FROM workouts WHERE client_id = ? ORDER BY date DESC LIMIT 1",
                (client_id,)
            )
            last_workout = self.cursor.fetchone()
            last_workout_date = last_workout[0] if last_workout else "Нет данных"

            # Самые популярные упражнения
            self.cursor.execute(
                """SELECT exercise_name, COUNT(*) as count 
                   FROM workouts WHERE client_id = ? 
                   GROUP BY exercise_name 
                   ORDER BY count DESC LIMIT 5""",
                (client_id,)
            )
            popular_exercises = self.cursor.fetchall()

            return {
                'total_workouts': total_workouts,
                'last_workout': last_workout_date,
                'popular_exercises': popular_exercises
            }
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return {}

    def display_clients(self, clients):
        """Отображение списка клиентов"""
        if not clients:
            print("Клиенты не найдены.")
            return

        print("\n--- Список клиентов ---")
        for client in clients:
            print(f"ID: {client[0]}, ФИО: {client[1]}, Дата рождения: {client[2]}, Телефон: {client[3]}")

    def display_workouts(self, workouts):
        """Отображение тренировок"""
        if not workouts:
            print("Тренировки не найдены.")
            return

        print("\n--- История тренировок ---")
        for workout in workouts:
            print(f"Дата: {workout[0]}, Упражнение: {workout[1]}")
            print(f"  Подходы: {workout[2]}, Повторения: {workout[3]}, Вес: {workout[4]}кг")
            if workout[5]:
                print(f"  Примечания: {workout[5]}")
            print()

    def display_stats(self, stats, client_name):
        """Отображение статистики"""
        print(f"\n--- Статистика клиента {client_name} ---")
        print(f"Всего тренировок: {stats['total_workouts']}")
        print(f"Последняя тренировка: {stats['last_workout']}")
        print("Популярные упражнения:")
        for exercise, count in stats['popular_exercises']:
            print(f"  {exercise}: {count} тренировок")

    def run(self):
        """Главный цикл приложения"""
        while True:
            if not self.is_authenticated():
                self.show_unauthorized_menu()
            else:
                self.show_authorized_menu()

    def show_unauthorized_menu(self):
        """Меню для неавторизованных пользователей"""
        print("\n" + "="*50)
        print("       СИСТЕМА УЧЕТА ТРЕНИРОВОК")
        print("="*50)
        print("1. Вход в систему")
        print("2. Регистрация тренера")
        print("3. Выход")
        
        choice = input("Выберите действие: ").strip()

        if choice == '1':
            self.handle_login()
        elif choice == '2':
            self.handle_registration()
        elif choice == '3':
            print("До свидания!")
            self.conn.close()
            exit()
        else:
            print("Неверный выбор. Попробуйте снова.")

    def handle_login(self):
        """Обработка входа"""
        login = input("Логин: ").strip()
        password = input("Пароль: ").strip()
        self.login_trainer(login, password)

    def handle_registration(self):
        """Обработка регистрации"""
        login = input("Придумайте логин: ").strip()
        password = input("Придумайте пароль: ").strip()
        full_name = input("Ваше полное имя: ").strip()
        self.register_trainer(login, password, full_name)

    def show_authorized_menu(self):
        """Меню для авторизованных тренеров"""
        print("\n" + "="*50)
        print(f"    ПАНЕЛЬ ТРЕНЕРА: {self.current_trainer['full_name']}")
        print("="*50)
        print("1. Мои клиенты")
        print("2. Добавить клиента")
        print("3. Поиск клиента")
        print("4. Добавить тренировку")
        print("5. Просмотреть тренировки клиента")
        print("6. Статистика клиента")
        print("7. Выход из системы")
        
        choice = input("Выберите действие: ").strip()

        if choice == '1':
            self.handle_show_clients()
        elif choice == '2':
            self.handle_add_client()
        elif choice == '3':
            self.handle_search_client()
        elif choice == '4':
            self.handle_add_workout()
        elif choice == '5':
            self.handle_show_workouts()
        elif choice == '6':
            self.handle_show_stats()
        elif choice == '7':
            self.logout()
        else:
            print("Неверный выбор. Попробуйте снова.")

    def handle_show_clients(self):
        """Показать всех клиентов"""
        clients = self.get_my_clients()
        self.display_clients(clients)

    def handle_add_client(self):
        """Добавить нового клиента"""
        full_name = input("ФИО клиента: ").strip()
        date_of_birth = input("Дата рождения (ГГГГ-ММ-ДД): ").strip()
        phone = input("Телефон (необязательно): ").strip()
        self.add_client(full_name, date_of_birth, phone)

    def handle_search_client(self):
        """Поиск клиента"""
        search_term = input("Введите имя для поиска: ").strip()
        clients = self.search_clients(search_term)
        self.display_clients(clients)

    def handle_add_workout(self):
        """Добавить тренировку"""
        clients = self.get_my_clients()
        if not clients:
            print("У вас нет клиентов.")
            return
            
        self.display_clients(clients)
        try:
            client_id = int(input("ID клиента: ").strip())
            exercise_name = input("Упражнение: ").strip()
            sets = int(input("Количество подходов: ").strip())
            reps = int(input("Количество повторений: ").strip())
            weight_kg = float(input("Вес (кг): ").strip())
            notes = input("Примечания (необязательно): ").strip()
            
            self.add_workout(client_id, exercise_name, sets, reps, weight_kg, notes)
        except ValueError:
            print("Ошибка: Проверьте правильность введенных данных.")
        except Exception as e:
            print(f"Ошибка: {e}")

    def handle_show_workouts(self):
        """Показать тренировки клиента"""
        clients = self.get_my_clients()
        if not clients:
            print("У вас нет клиентов.")
            return
            
        self.display_clients(clients)
        try:
            client_id = int(input("ID клиента: ").strip())
            workouts = self.get_client_workouts(client_id)
            self.display_workouts(workouts)
        except ValueError:
            print("Ошибка: Введите корректный ID клиента.")

    def handle_show_stats(self):
        """Показать статистику клиента"""
        clients = self.get_my_clients()
        if not clients:
            print("У вас нет клиентов.")
            return
            
        self.display_clients(clients)
        try:
            client_id = int(input("ID клиента: ").strip())
            # Находим имя клиента для отображения
            client_name = ""
            for client in clients:
                if client[0] == client_id:
                    client_name = client[1]
                    break
            
            stats = self.get_client_stats(client_id)
            self.display_stats(stats, client_name)
        except ValueError:
            print("Ошибка: Введите корректный ID клиента.")

if __name__ == "__main__":
    app = WorkoutTracker()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nПрограмма завершена.")
        app.conn.close()
