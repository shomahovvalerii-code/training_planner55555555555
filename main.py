import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.root.geometry("750x680")
        self.root.resizable(True, True)
        
        # Файл истории
        self.history_file = "password_history.json"
        self.history = []
        
        # Загрузка истории
        self.load_history()
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 14, "bold"))
        style.configure("Password.TLabel", font=("Courier", 16, "bold"), 
                       foreground="darkblue", background="lightgray")
        
    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🔐 Генератор случайных паролей", 
                               style="Title.TLabel")
        title_label.pack(pady=10)
        
        # --- Фрейм настроек ---
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки пароля", padding=15)
        settings_frame.pack(fill="x", pady=10)
        
        # Длина пароля
        length_frame = ttk.Frame(settings_frame)
        length_frame.pack(fill="x", pady=5)
        
        ttk.Label(length_frame, text="Длина пароля:", font=("Arial", 10)).pack(side="left", padx=5)
        
        self.length_var = tk.IntVar(value=16)
        self.length_scale = ttk.Scale(length_frame, from_=4, to=64, 
                                     orient="horizontal", variable=self.length_var,
                                     command=self.update_length_label)
        self.length_scale.pack(side="left", fill="x", expand=True, padx=10)
        
        self.length_label = ttk.Label(length_frame, text="16", width=3, 
                                     font=("Arial", 10, "bold"))
        self.length_label.pack(side="left", padx=5)
        
        # Чекбоксы для типов символов
        checkboxes_frame = ttk.LabelFrame(settings_frame, text="Типы символов", padding=10)
        checkboxes_frame.pack(fill="x", pady=10)
        
        # Первый ряд
        row1_frame = ttk.Frame(checkboxes_frame)
        row1_frame.pack(fill="x", pady=3)
        
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(row1_frame, text="Заглавные буквы (A-Z)", 
                       variable=self.use_uppercase).pack(side="left", padx=10)
        ttk.Checkbutton(row1_frame, text="Строчные буквы (a-z)", 
                       variable=self.use_lowercase).pack(side="left", padx=10)
        
        # Второй ряд
        row2_frame = ttk.Frame(checkboxes_frame)
        row2_frame.pack(fill="x", pady=3)
        
        ttk.Checkbutton(row2_frame, text="Цифры (0-9)", 
                       variable=self.use_digits).pack(side="left", padx=10)
        ttk.Checkbutton(row2_frame, text="Спецсимволы (!@#$%^&*)", 
                       variable=self.use_special).pack(side="left", padx=10)
        
        # Дополнительные опции
        options_frame = ttk.LabelFrame(settings_frame, text="Дополнительные настройки", padding=10)
        options_frame.pack(fill="x", pady=5)
        
        self.exclude_similar = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.require_all_types = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Исключить похожие символы (i, l, 1, L, o, 0, O)", 
                       variable=self.exclude_similar).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Избегать неоднозначных символов ({ } [ ] ( ) / \\ ' \" ` ~ , ; : . < >)", 
                       variable=self.exclude_ambiguous).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Обязательно использовать все выбранные типы символов", 
                       variable=self.require_all_types).pack(anchor="w", pady=2)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.pack(fill="x", pady=15)
        
        self.generate_btn = ttk.Button(buttons_frame, text="🎲 Сгенерировать пароль", 
                                      command=self.generate_password, width=25)
        self.generate_btn.pack(side="left", padx=5)
        
        self.copy_btn = ttk.Button(buttons_frame, text="📋 Копировать в буфер", 
                                  command=self.copy_to_clipboard, width=20)
        self.copy_btn.pack(side="left", padx=5)
        
        self.clear_btn = ttk.Button(buttons_frame, text="🗑️ Очистить", 
                                   command=self.clear_password, width=15)
        self.clear_btn.pack(side="left", padx=5)
        
        # --- Отображение пароля ---
        password_frame = ttk.LabelFrame(main_frame, text="Сгенерированный пароль", padding=10)
        password_frame.pack(fill="x", pady=10)
        
        self.password_var = tk.StringVar(value="Нажмите кнопку для генерации...")
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var,
                                       font=("Courier", 16, "bold"), justify="center",
                                       state="readonly")
        self.password_entry.pack(fill="x", pady=5, ipady=5)
        
        # Информация о пароле
        info_frame = ttk.Frame(password_frame)
        info_frame.pack(fill="x", pady=5)
        
        # Длина
        ttk.Label(info_frame, text="Длина:").pack(side="left", padx=5)
        self.stats_length_var = tk.StringVar(value="-")
        ttk.Label(info_frame, textvariable=self.stats_length_var, width=5).pack(side="left", padx=5)
        
        # Надежность
        ttk.Label(info_frame, text="Надёжность:").pack(side="left", padx=5)
        self.strength_var = tk.StringVar(value="-")
        self.strength_label = ttk.Label(info_frame, textvariable=self.strength_var,
                                       font=("Arial", 10, "bold"), width=15)
        self.strength_label.pack(side="left", padx=5)
        
        # Прогресс-бар надежности
        self.strength_bar = ttk.Progressbar(info_frame, length=150, mode="determinate")
        self.strength_bar.pack(side="left", padx=10)
        
        # --- История паролей ---
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, pady=10)
        
        # Таблица истории
        columns = ("date", "password", "length", "chars", "strength")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, 
                                        show="headings", height=8)
        
        self.history_tree.heading("date", text="Дата")
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("chars", text="Типы символов")
        self.history_tree.heading("strength", text="Надёжность")
        
        self.history_tree.column("date", width=140, anchor="center")
        self.history_tree.column("password", width=200)
        self.history_tree.column("length", width=60, anchor="center")
        self.history_tree.column("chars", width=120, anchor="center")
        self.history_tree.column("strength", width=100, anchor="center")
        
        # Скроллбары
        y_scroll = ttk.Scrollbar(history_frame, orient="vertical", 
                                command=self.history_tree.yview)
        x_scroll = ttk.Scrollbar(history_frame, orient="horizontal", 
                                command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=y_scroll.set, 
                                   xscrollcommand=x_scroll.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        
        # Кнопки управления историей
        history_buttons = ttk.Frame(main_frame)
        history_buttons.pack(fill="x", pady=5)
        
        ttk.Button(history_buttons, text="📋 Копировать выбранный", 
                  command=self.copy_selected_from_history).pack(side="left", padx=5)
        ttk.Button(history_buttons, text="🗑️ Очистить историю", 
                  command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(history_buttons, text="📤 Экспорт в файл", 
                  command=self.export_history).pack(side="left", padx=5)
        
        # Отображаем историю
        self.display_history()
    
    def update_length_label(self, *args):
        """Обновление метки длины пароля"""
        self.length_label.config(text=str(int(self.length_var.get())))
    
    def get_character_sets(self):
        """Получение наборов символов для генерации"""
        sets = {}
        
        if self.use_uppercase.get():
            chars = string.ascii_uppercase
            if self.exclude_similar.get():
                chars = chars.replace('O', '')
            sets['uppercase'] = chars
        
        if self.use_lowercase.get():
            chars = string.ascii_lowercase
            if self.exclude_similar.get():
                chars = chars.replace('l', '').replace('o', '')
            sets['lowercase'] = chars
        
        if self.use_digits.get():
            chars = string.digits
            if self.exclude_similar.get():
                chars = chars.replace('0', '').replace('1', '')
            sets['digits'] = chars
        
        if self.use_special.get():
            chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if self.exclude_ambiguous.get():
                chars = "!@#$%^&*_+-="
            sets['special'] = chars
        
        return sets
    
    def generate_password(self):
        """Генерация пароля с учетом настроек"""
        char_sets = self.get_character_sets()
        
        if not char_sets:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return
        
        length = int(self.length_var.get())
        
        # Проверка длины
        if length < 4 or length > 64:
            messagebox.showerror("Ошибка", "Длина пароля должна быть от 4 до 64 символов!")
            return
        
        # Все доступные символы
        all_chars = ''.join(char_sets.values())
        
        if self.require_all_types.get():
            # Если требуется использовать все типы
            password_chars = []
            
            # Добавляем по одному символу каждого типа
            for char_set in char_sets.values():
                password_chars.append(random.choice(char_set))
            
            # Заполняем остальное случайными символами
            remaining_length = length - len(password_chars)
            if remaining_length > 0:
                password_chars.extend(random.choice(all_chars) 
                                     for _ in range(remaining_length))
            
            # Перемешиваем
            random.shuffle(password_chars)
            password = ''.join(password_chars)
        else:
            # Простая генерация
            password = ''.join(random.choice(all_chars) for _ in range(length))
        
        # Отображаем пароль
        self.password_var.set(password)
        
        # Вычисляем статистику
        self.update_password_stats(password, char_sets)
        
        # Добавляем в историю
        self.add_to_history(password, char_sets)
        
        return password
    
    def update_password_stats(self, password, char_sets):
        """Обновление статистики пароля"""
        length = len(password)
        self.stats_length_var.set(str(length))
        
        # Оценка надежности
        score = 0
        
        # Длина
        if length >= 16:
            score += 4
        elif length >= 12:
            score += 3
        elif length >= 8:
            score += 2
        else:
            score += 1
        
        # Разнообразие символов
        types_used = 0
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        types_used = sum([has_upper, has_lower, has_digit, has_special])
        score += types_used * 2
        
        # Определение уровня
        if score >= 10:
            strength = "Отличный"
            color = "darkgreen"
            bar_value = 100
        elif score >= 8:
            strength = "Хороший"
            color = "green"
            bar_value = 80
        elif score >= 6:
            strength = "Средний"
            color = "orange"
            bar_value = 60
        elif score >= 4:
            strength = "Слабый"
            color = "red"
            bar_value = 40
        else:
            strength = "Очень слабый"
            color = "darkred"
            bar_value = 20
        
        self.strength_var.set(strength)
        self.strength_label.config(foreground=color)
        self.strength_bar["value"] = bar_value
    
    def add_to_history(self, password, char_sets):
        """Добавление пароля в историю"""
        # Определяем типы используемых символов
        types = []
        if 'uppercase' in char_sets:
            types.append("A-Z")
        if 'lowercase' in char_sets:
            types.append("a-z")
        if 'digits' in char_sets:
            types.append("0-9")
        if 'special' in char_sets:
            types.append("!@#")
        
        entry = {
            "date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "password": password,
            "length": len(password),
            "char_types": ", ".join(types),
            "strength": self.strength_var.get()
        }
        
        self.history.append(entry)
        
        # Ограничиваем историю последними 100 записями
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self.save_history()
        self.display_history()
    
    def display_history(self):
        """Отображение истории в таблице"""
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавление записей (новые сверху)
        for entry in reversed(self.history):
            self.history_tree.insert("", "end", values=(
                entry["date"],
                entry["password"],
                entry["length"],
                entry["char_types"],
                entry["strength"]
            ))
    
    def copy_to_clipboard(self):
        """Копирование текущего пароля в буфер обмена"""
        password = self.password_var.get()
        if password and password != "Нажмите кнопку для генерации...":
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
    
    def copy_selected_from_history(self):
        """Копирование выбранного пароля из истории"""
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пароль из истории!")
            return
        
        password = self.history_tree.item(selected[0])['values'][1]
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
    
    def clear_password(self):
        """Очистка поля с паролем"""
        self.password_var.set("Нажмите кнопку для генерации...")
        self.stats_length_var.set("-")
        self.strength_var.set("-")
        self.strength_bar["value"] = 0
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Удалить всю историю паролей?"):
            self.history = []
            self.save_history()
            self.display_history()
            messagebox.showinfo("Успех", "История очищена!")
    
    def export_history(self):
        """Экспорт истории в текстовый файл"""
        if not self.history:
            messagebox.showwarning("Предупреждение", "История пуста!")
            return
        
        filename = f"passwords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("История сгенерированных паролей\n")
                f.write("=" * 60 + "\n\n")
                
                for i, entry in enumerate(self.history, 1):
                    f.write(f"#{i}\n")
                    f.write(f"Дата: {entry['date']}\n")
                    f.write(f"Пароль: {entry['password']}\n")
                    f.write(f"Длина: {entry['length']} символов\n")
                    f.write(f"Типы символов: {entry['char_types']}\n")
                    f.write(f"Надёжность: {entry['strength']}\n")
                    f.write("-" * 40 + "\n")
            
            messagebox.showinfo("Успех", f"История экспортирована в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")
    
    def save_history(self):
        """Сохранение истории в JSON"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
    
    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()