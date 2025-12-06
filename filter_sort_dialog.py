import tkinter as tk
from tkinter import ttk


class FilterSortDialog:
    def __init__(self, parent, db, table, column_names=None):
        self.db = db
        self.table = table
        self.column_names = column_names or {}
        self.filters = []
        self.sort_column = ""
        self.sort_direction = "ASC"
        self.filter_widgets = []

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Фильтр и сортировка: {table}")
        self.dialog.geometry("600x500")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        filter_frame = ttk.LabelFrame(main_frame, text="Фильтры (несколько условий объединяются через И)")
        filter_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(filter_buttons_frame, text="+ Добавить условие фильтра",
                   command=self.add_filter_row).pack(side=tk.LEFT, padx=5)

        self.filter_container = ttk.Frame(filter_frame)
        self.filter_container.pack(fill=tk.BOTH, expand=True)

        self.add_filter_row()

        sort_frame = ttk.LabelFrame(main_frame, text="Сортировка")
        sort_frame.pack(fill=tk.X, pady=5)

        columns = self.db.get_table_columns(self.table)
        russian_columns = [self.column_names.get(col[0], col[0]) for col in columns]

        ttk.Label(sort_frame, text="Поле сортировки:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.sort_column_combo = ttk.Combobox(sort_frame)
        self.sort_column_combo['values'] = russian_columns
        self.sort_column_combo.grid(row=0, column=1, sticky=tk.W + tk.E, padx=5, pady=2)

        ttk.Label(sort_frame, text="Направление:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.sort_direction_combo = ttk.Combobox(sort_frame, values=["По возрастанию", "По убыванию"])
        self.sort_direction_combo.grid(row=1, column=1, sticky=tk.W + tk.E, padx=5, pady=2)
        self.sort_direction_combo.set("По возрастанию")


        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Применить", command=self.apply).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Очистить фильтры", command=self.clear_filters).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT)

    def add_filter_row(self):
        row_index = len(self.filter_widgets)
        row_frame = ttk.Frame(self.filter_container)
        row_frame.pack(fill=tk.X, pady=2, padx=5)

        columns = self.db.get_table_columns(self.table)
        russian_columns = [self.column_names.get(col[0], col[0]) for col in columns]
        column_combo = ttk.Combobox(row_frame, values=russian_columns, width=20)
        column_combo.pack(side=tk.LEFT, padx=2)
        if russian_columns:
            column_combo.set(russian_columns[0])
        operator_combo = ttk.Combobox(row_frame, values=[
            "равно", "не равно", "содержит", "не содержит",
            "больше", "меньше", "больше или равно", "меньше или равно"
        ], width=15)
        operator_combo.pack(side=tk.LEFT, padx=2)
        operator_combo.set("содержит")
        value_entry = ttk.Entry(row_frame, width=20)
        value_entry.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        delete_btn = ttk.Button(row_frame, text="×", width=3,
                                command=lambda: self.remove_filter_row(row_frame))
        delete_btn.pack(side=tk.LEFT, padx=2)

        self.filter_widgets.append({
            'frame': row_frame,
            'column': column_combo,
            'operator': operator_combo,
            'value': value_entry
        })

    def remove_filter_row(self, row_frame):
        for i, widget in enumerate(self.filter_widgets):
            if widget['frame'] == row_frame:
                widget['frame'].destroy()
                self.filter_widgets.pop(i)
                break

    def clear_filters(self):
        for widget in self.filter_widgets:
            widget['frame'].destroy()
        self.filter_widgets = []
        self.add_filter_row()

    def apply(self):
        self.filters = []
        for widget in self.filter_widgets:
            column_russian = widget['column'].get().strip()
            operator = widget['operator'].get()
            value = widget['value'].get().strip()

            if not column_russian or not value:
                continue

            column_english = None
            for eng_name, rus_name in self.column_names.items():
                if rus_name == column_russian:
                    column_english = eng_name
                    break

            if not column_english:
                continue

            op_map = {
                "равно": "=",
                "не равно": "!=",
                "содержит": "LIKE",
                "не содержит": "NOT LIKE",
                "больше": ">",
                "меньше": "<",
                "больше или равно": ">=",
                "меньше или равно": "<="
            }
            sql_operator = op_map.get(operator, "LIKE")

            if sql_operator in ["LIKE", "NOT LIKE"]:
                formatted_value = f"'%{value}%'"
            else:
                formatted_value = f"'{value}'"

            self.filters.append(f"{column_english} {sql_operator} {formatted_value}")

        sort_russian = self.sort_column_combo.get().strip()
        if sort_russian:
            for eng_name, rus_name in self.column_names.items():
                if rus_name == sort_russian:
                    self.sort_column = eng_name
                    break

        direction_text = self.sort_direction_combo.get()
        self.sort_direction = "DESC" if direction_text == "По убыванию" else "ASC"

        self.dialog.destroy()