import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherRecord:
    """Класс модели записи погоды"""

    def __init__(self, date: str, temperature: float, description: str, precipitation: bool):
        self.date = date
        self.temperature = temperature
        self.description = description
        self.precipitation = precipitation
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        """Преобразование в словарь для JSON"""
        return {
            "date": self.date,
            "temperature": self.temperature,
            "description": self.description,
            "precipitation": self.precipitation,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WeatherRecord':
        """Создание записи из словаря"""
        record = cls(
            data["date"],
            data["temperature"],
            data["description"],
            data["precipitation"]
        )
        record.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return record


class WeatherDiary:
    """Главное приложение Дневник погоды"""

    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("1000x650")
        self.root.resizable(True, True)

        # Данные
        self.records = []
        self.data_file = "weather_data.json"

        # Загрузка сохраненных записей
        self.load_records()

        # Создание интерфейса
        self.create_widgets()

        # Обновление отображения
        self.refresh_records_list()

    def create_widgets(self):
        """Создание GUI интерфейса"""

        # Главная рамка
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="🌤️ Weather Diary - Дневник погоды",
                                font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Левая панель - форма добавления записи
        left_frame = ttk.LabelFrame(main_frame, text="➕ Добавить запись погоды", padding="15")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(1, weight=1)

        # Поля ввода
        # Дата
        ttk.Label(left_frame, text="📅 Дата:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.date_entry = ttk.Entry(left_frame, width=25, font=("Arial", 10))
        self.date_entry.grid(row=0, column=1, pady=8, padx=(10, 0), sticky=(tk.W, tk.E))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Подсказка для даты
        ttk.Label(left_frame, text="(Формат: ГГГГ-ММ-ДД)", font=("Arial", 8), foreground="gray").grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        # Температура
        ttk.Label(left_frame, text="🌡️ Температура (°C):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.temp_entry = ttk.Entry(left_frame, width=25, font=("Arial", 10))
        self.temp_entry.grid(row=2, column=1, pady=8, padx=(10, 0), sticky=(tk.W, tk.E))

        # Описание погоды
        ttk.Label(left_frame, text="📝 Описание погоды:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.desc_text = tk.Text(left_frame, height=4, width=30, font=("Arial", 10))
        self.desc_text.grid(row=3, column=1, pady=8, padx=(10, 0), sticky=(tk.W, tk.E))

        # Осадки
        ttk.Label(left_frame, text="☔ Осадки:", font=("Arial", 10)).grid(row=4, column=0, sticky=tk.W, pady=8)
        self.precipitation_var = tk.BooleanVar()
        self.precipitation_check = ttk.Checkbutton(left_frame, text="Да", variable=self.precipitation_var)
        self.precipitation_check.grid(row=4, column=1, sticky=tk.W, pady=8, padx=(10, 0))

        # Кнопка добавления
        ttk.Button(left_frame, text="➕ Добавить запись", command=self.add_record, width=25).grid(row=5, column=0, columnspan=2, pady=20)

        # Статистика
        stats_frame = ttk.LabelFrame(left_frame, text="📊 Статистика", padding="10")
        stats_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        stats_frame.columnconfigure(0, weight=1)

        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 10), justify=tk.LEFT)
        self.stats_label.pack()

        # Правая панель - список записей и фильтры
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # Фильтры
        filter_frame = ttk.LabelFrame(right_frame, text="🔍 Фильтрация записей", padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)

        # Фильтр по дате
        ttk.Label(filter_frame, text="📅 Дата:").grid(row=0, column=0, padx=5)
        self.filter_date = ttk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.filter_date.insert(0, "")

        ttk.Button(filter_frame, text="Применить", command=self.refresh_records_list, width=10).grid(row=0, column=2, padx=5)
        ttk.Button(filter_frame, text="Очистить", command=self.clear_date_filter, width=10).grid(row=0, column=3, padx=5)

        # Фильтр по температуре
        ttk.Label(filter_frame, text="🌡️ Температура:").grid(row=1, column=0, padx=5, pady=5)
        self.filter_temp_condition = ttk.Combobox(filter_frame, values=["Все", "> +10°C", "< +10°C", "> +20°C", "< 0°C", "0°C - +10°C"],
                                                  width=12, state="readonly")
        self.filter_temp_condition.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E))
        self.filter_temp_condition.set("Все")

        ttk.Button(filter_frame, text="Применить", command=self.refresh_records_list, width=10).grid(row=1, column=2, padx=5)
        ttk.Button(filter_frame, text="Сбросить все", command=self.reset_filters, width=10).grid(row=1, column=3, padx=5)

        # Таблица записей
        table_frame = ttk.LabelFrame(right_frame, text="📋 Записи погоды", padding="10")
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Создание таблицы
        columns = ("Дата", "Температура", "Осадки", "Описание", "Время создания")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Настройка колонок
        self.tree.heading("Дата", text="📅 Дата")
        self.tree.heading("Температура", text="🌡️ Температура")
        self.tree.heading("Осадки", text="☔ Осадки")
        self.tree.heading("Описание", text="📝 Описание")
        self.tree.heading("Время создания", text="🕐 Время создания")

        self.tree.column("Дата", width=100)
        self.tree.column("Температура", width=100)
        self.tree.column("Осадки", width=80)
        self.tree.column("Описание", width=300)
        self.tree.column("Время создания", width=140)

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Кнопки управления
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=2, column=0, pady=10)

        ttk.Button(button_frame, text="🗑️ Удалить выбранную запись", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Редактировать", command=self.edit_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Сохранить данные", command=self.save_records).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📁 Загрузить данные", command=self.load_records).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Статистика", command=self.show_statistics).pack(side=tk.LEFT, padx=5)

        # Привязка двойного щелчка для редактирования
        self.tree.bind("<Double-1>", lambda event: self.edit_record())

        # Привязка Enter для добавления
        self.temp_entry.bind('<Return>', lambda event: self.add_record())

        # Обновление статистики
        self.update_stats()

    def validate_date(self, date_str: str) -> bool:
        """Проверка корректности даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_record(self):
        """Добавление новой записи"""
        # Получение данных
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        precipitation = self.precipitation_var.get()

        # Валидация даты
        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой!")
            return

        # Негативный тест: неверный формат даты
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте формат: ГГГГ-ММ-ДД\nПример: 2024-12-25")
            return

        # Валидация температуры
        if not temp_str:
            messagebox.showerror("Ошибка", "Температура не может быть пустой!")
            return

        try:
            temperature = float(temp_str)
            # Граничные тесты
            if temperature < -50:
                if not messagebox.askyesno("Предупреждение", "Температура ниже -50°C. Это корректно?"):
                    return
            if temperature > 50:
                if not messagebox.askyesno("Предупреждение", "Температура выше 50°C. Это корректно?"):
                    return
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return

        # Валидация описания
        if not description:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return

        # Создание записи
        record = WeatherRecord(date, temperature, description, precipitation)
        self.records.append(record)

        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.precipitation_var.set(False)

        # Сохранение и обновление
        self.save_records()
        self.refresh_records_list()

        messagebox.showinfo("Успех", f"Запись о погоде на {date} добавлена!")

    def delete_record(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return

        item = self.tree.item(selected[0])
        date = item['values'][0]
        temp = item['values'][1]

        if messagebox.askyesno("Подтверждение", f"Удалить запись о погоде на {date} (температура {temp}°C)?"):
            # Удаление из списка
            for i, record in enumerate(self.records):
                if record.date == date and record.temperature == float(temp):
                    del self.records[i]
                    break

            self.save_records()
            self.refresh_records_list()
            messagebox.showinfo("Успех", "Запись удалена!")

    def edit_record(self):
        """Редактирование выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования!")
            return

        item = self.tree.item(selected[0])
        old_date = item['values'][0]
        old_temp = float(item['values'][1])

        # Поиск записи
        record = None
        for r in self.records:
            if r.date == old_date and r.temperature == old_temp:
                record = r
                break

        if not record:
            return

        # Диалог редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование записи погоды")
        edit_window.geometry("450x450")
        edit_window.resizable(False, False)

        # Центрирование
        edit_window.transient(self.root)
        edit_window.grab_set()

        # Поля редактирования
        ttk.Label(edit_window, text="📅 Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).pack(pady=(20, 5))
        date_entry = ttk.Entry(edit_window, width=30, font=("Arial", 10))
        date_entry.insert(0, record.date)
        date_entry.pack(pady=5)

        ttk.Label(edit_window, text="🌡️ Температура (°C):", font=("Arial", 10)).pack(pady=5)
        temp_entry = ttk.Entry(edit_window, width=30, font=("Arial", 10))
        temp_entry.insert(0, str(record.temperature))
        temp_entry.pack(pady=5)

        ttk.Label(edit_window, text="📝 Описание погоды:", font=("Arial", 10)).pack(pady=5)
        desc_text = tk.Text(edit_window, height=5, width=35, font=("Arial", 10))
        desc_text.insert("1.0", record.description)
        desc_text.pack(pady=5)

        ttk.Label(edit_window, text="☔ Осадки:", font=("Arial", 10)).pack(pady=5)
        precip_var = tk.BooleanVar(value=record.precipitation)
        precip_check = ttk.Checkbutton(edit_window, text="Да", variable=precip_var)
        precip_check.pack(pady=5)

        def save_edit():
            try:
                new_date = date_entry.get().strip()
                new_temp = float(temp_entry.get().strip())
                new_desc = desc_text.get("1.0", tk.END).strip()
                new_precip = precip_var.get()

                # Валидация
                if not new_date:
                    messagebox.showerror("Ошибка", "Дата не может быть пустой!")
                    return
                if not self.validate_date(new_date):
                    messagebox.showerror("Ошибка", "Неверный формат даты!")
                    return
                if not new_desc:
                    messagebox.showerror("Ошибка", "Описание не может быть пустым!")
                    return
                if new_temp < -50 or new_temp > 50:
                    if not messagebox.askyesno("Предупреждение", f"Температура {new_temp}°C аномальна. Продолжить?"):
                        return

                # Обновление записи
                record.date = new_date
                record.temperature = new_temp
                record.description = new_desc
                record.precipitation = new_precip

                self.save_records()
                self.refresh_records_list()
                edit_window.destroy()
                messagebox.showinfo("Успех", "Запись обновлена!")

            except ValueError:
                messagebox.showerror("Ошибка", "Температура должна быть числом!")

        ttk.Button(edit_window, text="Сохранить", command=save_edit, width=20).pack(pady=20)

    def refresh_records_list(self):
        """Обновление списка записей с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Фильтрация записей
        filtered_records = self.apply_filters()

        # Добавление записей в таблицу
        for record in filtered_records:
            precipitation = "Да" if record.precipitation else "Нет"
            self.tree.insert("", tk.END, values=(
                record.date,
                f"{record.temperature:.1f}°C",
                precipitation,
                record.description[:50] + "..." if len(record.description) > 50 else record.description,
                record.created_at
            ))

        # Обновление статистики
        self.update_stats()

    def apply_filters(self):
        """Применение фильтров к списку записей"""
        filtered = self.records.copy()

        # Фильтр по дате
        date_filter = self.filter_date.get().strip()
        if date_filter:
            if self.validate_date(date_filter):
                filtered = [r for r in filtered if r.date == date_filter]
            else:
                messagebox.showwarning("Предупреждение", "Неверный формат даты в фильтре!")

        # Фильтр по температуре
        temp_filter = self.filter_temp_condition.get()
        if temp_filter == "> +10°C":
            filtered = [r for r in filtered if r.temperature > 10]
        elif temp_filter == "< +10°C":
            filtered = [r for r in filtered if r.temperature < 10]
        elif temp_filter == "> +20°C":
            filtered = [r for r in filtered if r.temperature > 20]
        elif temp_filter == "< 0°C":
            filtered = [r for r in filtered if r.temperature < 0]
        elif temp_filter == "0°C - +10°C":
            filtered = [r for r in filtered if 0 <= r.temperature <= 10]

        return filtered

    def clear_date_filter(self):
        """Очистка фильтра по дате"""
        self.filter_date.delete(0, tk.END)
        self.refresh_records_list()

    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_date.delete(0, tk.END)
        self.filter_temp_condition.set("Все")
        self.refresh_records_list()

    def update_stats(self):
        """Обновление статистики"""
        total_records = len(self.records)
        if total_records == 0:
            self.stats_label.config(text="Нет записей")
            return

        avg_temp = sum(r.temperature for r in self.records) / total_records
        max_temp = max(r.temperature for r in self.records)
        min_temp = min(r.temperature for r in self.records)
        rainy_days = sum(1 for r in self.records if r.precipitation)

        stats_text = f"""📊 Статистика:
📝 Всего записей: {total_records}
🌡️ Средняя температура: {avg_temp:.1f}°C
🔥 Максимальная: {max_temp:.1f}°C
❄️ Минимальная: {min_temp:.1f}°C
☔ Дней с осадками: {rainy_days} ({rainy_days*100//total_records if total_records>0 else 0}%)"""

        self.stats_label.config(text=stats_text)

    def show_statistics(self):
        """Показать подробную статистику в отдельном окне"""
        if not self.records:
            messagebox.showinfo("Статистика", "Нет записей для анализа!")
            return

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Детальная статистика погоды")
        stats_window.geometry("600x500")
        stats_window.resizable(False, False)

        stats_window.transient(self.root)
        stats_window.grab_set()

        # Подсчет статистики
        total = len(self.records)
        avg_temp = sum(r.temperature for r in self.records) / total
        max_temp = max(r.temperature for r in self.records)
        min_temp = min(r.temperature for r in self.records)
        rainy = sum(1 for r in self.records if r.precipitation)

        # Температурные категории
        hot = sum(1 for r in self.records if r.temperature > 20)
        warm = sum(1 for r in self.records if 10 <= r.temperature <= 20)
        cool = sum(1 for r in self.records if 0 <= r.temperature < 10)
        cold = sum(1 for r in self.records if r.temperature < 0)

        # Самые частые описания
        descriptions = {}
        for r in self.records:
            words = r.description.lower().split()
            for word in words[:3]:
                descriptions[word] = descriptions.get(word, 0) + 1

        top_words = sorted(descriptions.items(), key=lambda x: x[1], reverse=True)[:5]

        stats_text = f"""📊 ПОДРОБНАЯ СТАТИСТИКА ПОГОДЫ
{'='*50}

📝 Общее количество записей: {total}

🌡️ ТЕМПЕРАТУРА:
{'='*50}
  • Средняя: {avg_temp:.1f}°C
  • Максимальная: {max_temp:.1f}°C
  • Минимальная: {min_temp:.1f}°C
  • Диапазон: {min_temp:.1f}°C - {max_temp:.1f}°C

🌡️ КАТЕГОРИИ ТЕМПЕРАТУР:
{'='*50}
  • Жарко (>20°C): {hot} дней ({hot*100//total}%)
  • Тепло (10-20°C): {warm} дней ({warm*100//total}%)
  • Прохладно (0-10°C): {cool} дней ({cool*100//total}%)
  • Холодно (<0°C): {cold} дней ({cold*100//total}%)

☔ ОСАДКИ:
{'='*50}
  • Дней с осадками: {rainy} ({rainy*100//total}%)
  • Дней без осадков: {total-rainy} ({(total-rainy)*100//total}%)

📝 ЧАСТЫЕ СЛОВА В ОПИСАНИЯХ:
{'='*50}"""

        for word, count in top_words:
            stats_text += f"\n  • {word}: {count} раз"

        # Текстовое поле с прокруткой
        text_frame = ttk.Frame(stats_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(stats_window, text="Закрыть", command=stats_window.destroy).pack(pady=10)

    def save_records(self):
        """Сохранение записей в JSON файл"""
        try:
            data = [record.to_dict() for record in self.records]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            return False

    def load_records(self):
        """Загрузка записей из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = [WeatherRecord.from_dict(item) for item in data]
                self.refresh_records_list()
                messagebox.showinfo("Успех", f"Загружено {len(self.records)} записей!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Файл с данными не найден!")


def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()


if __name__ == "__main__":
    main()
