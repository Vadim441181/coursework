from ttkbootstrap import Style
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox

from database import Database
from edit_dialog import EditDialog
from filter_sort_dialog import FilterSortDialog
from route_transit_form import RouteTransitForm
from report_dialog import ReportDialog


class AirportApp:
    def __init__(self, root):
        self.root = root
        self.style = Style(theme="flatly")
        self.root.title("Система управления аэропортом")
        self.root.geometry("1200x700")

        self.db = Database()
        self.current_table = None
        self.current_data = []
        self.current_filters = ""
        self.current_sort = ""

        self.table_names = {
            'airports': 'Аэропорты',
            'airlines': 'Авиакомпании',
            'aircrafts': 'Самолеты',
            'positions': 'Должности',
            'crews': 'Экипажи',
            'services': 'Службы',
            'staff': 'Персонал',
            'routes': 'Маршруты',
            'transit_routes': 'Транзитные маршруты'
        }

        self.column_names = {
            'airport_code': 'Код аэропорта',
            'airport_name': 'Название аэропорта',
            'city': 'Город',
            'country': 'Страна',
            'phone_number': 'Телефон',
            'timezone': 'Часовой пояс',

            'airline_code': 'Код авиакомпании',
            'airline_name': 'Название авиакомпании',

            'aircraft_code': 'Код самолета',
            'aircraft_name': 'Название самолета',
            'capacity': 'Вместимость',
            'range_km': 'Дальность (км)',

            'position_id': 'Код должности',
            'position_name': 'Название должности',

            'crew_id': 'Код экипажа',
            'crew_name': 'Название экипажа',

            'service_id': 'Код службы',
            'service_name': 'Название службы',

            'inn': 'ИНН',
            'full_name': 'ФИО',

            'route_code': 'Код маршрута',
            'departure_airport': 'Аэропорт вылета',
            'arrival_airport': 'Аэропорт назначения',
            'base_airport': 'Базовый аэропорт',
            'departure_time': 'Время вылета',
            'arrival_time': 'Время прибытия',
            'flight_time': 'Время полета',

            'stop_num': 'Номер остановки',
            'stop_airport': 'Аэропорт остановки',
            'arrival': 'Время прибытия',
            'departure': 'Время вылета'
        }

        self.create_widgets()
        self.load_table_list()


    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 10))

        tables_frame = ttk.Labelframe(left_frame, text="Таблицы базы данных", bootstyle="secondary")
        tables_frame.pack(fill=X, pady=(0, 10))

        self.table_list = tk.Listbox(tables_frame, width=22, height=18)
        self.table_list.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.table_list.bind('<<ListboxSelect>>', self.on_table_select)

        reports_frame = ttk.Labelframe(left_frame, text="Отчеты", bootstyle="secondary")
        reports_frame.pack(fill=X, pady=(0, 10))

        report_buttons = [
            ("Маршруты по назначению", self.report_routes_by_destination),
            ("Ближайшие рейсы", self.report_upcoming_flights),
            ("Флот авиакомпаний", self.report_airlines_fleet)
        ]

        for text, cmd in report_buttons:
            ttk.Button(reports_frame, text=text, bootstyle="info", command=cmd).pack(fill=X, pady=2)

        forms_frame = ttk.Labelframe(left_frame, text="Специальные формы", bootstyle="secondary")
        forms_frame.pack(fill=X)

        ttk.Button(forms_frame, text="Маршрут + Остановки",
                   bootstyle="success", command=self.open_route_transit_form).pack(fill=X, pady=2)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=X, pady=(0, 10))

        buttons_left = ttk.Frame(control_frame)
        buttons_left.pack(side=LEFT)

        ttk.Button(buttons_left, text="Добавить", bootstyle="success", command=self.add_record).pack(side=LEFT, padx=5)
        ttk.Button(buttons_left, text="Редактировать", bootstyle="warning", command=self.edit_record).pack(side=LEFT, padx=5)
        ttk.Button(buttons_left, text="Удалить", bootstyle="danger", command=self.delete_record).pack(side=LEFT, padx=5)
        ttk.Button(buttons_left, text="Фильтр/Сортировка", bootstyle="info",
                   command=self.open_filter_dialog).pack(side=LEFT, padx=5)
        ttk.Button(buttons_left, text="Сброс", bootstyle="secondary", command=self.reset_view).pack(side=LEFT, padx=5)

        search_frame = ttk.Labelframe(control_frame, text="Поиск", bootstyle="secondary")
        search_frame.pack(side=RIGHT, fill=X, expand=True, padx=10)

        ttk.Label(search_frame, text="Столбец:").pack(side=LEFT, padx=5)
        self.search_column = ttk.Combobox(search_frame, width=18)
        self.search_column.pack(side=LEFT, padx=5)

        ttk.Label(search_frame, text="Значение:").pack(side=LEFT, padx=5)
        self.search_value = ttk.Entry(search_frame, width=20)
        self.search_value.pack(side=LEFT, padx=5)
        self.search_value.bind("<Return>", lambda e: self.search_records())

        ttk.Button(search_frame, text="Найти", bootstyle="info", command=self.search_records).pack(side=LEFT, padx=5)
        ttk.Button(search_frame, text="Очистить", bootstyle="secondary", command=self.clear_search).pack(side=LEFT, padx=5)

        table_frame = ttk.Frame(right_frame)
        table_frame.pack(fill=BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, bootstyle="dark")
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.status_bar = ttk.Label(right_frame, text="Готов к работе", anchor=W, bootstyle="inverse-secondary")
        self.status_bar.pack(fill=X, pady=(5, 0))


    def get_russian_table_name(self, t): return self.table_names.get(t, t)

    def get_russian_column_name(self, c): return self.column_names.get(c, c)

    def load_table_list(self):
        tables = [
            'airports', 'airlines', 'aircrafts', 'positions',
            'crews', 'services', 'staff', 'routes', 'transit_routes'
        ]
        self.table_list.delete(0, END)
        for tbl in tables:
            self.table_list.insert(END, self.get_russian_table_name(tbl))

    def on_table_select(self, event):
        selection = self.table_list.curselection()
        if not selection: return

        rus_name = self.table_list.get(selection[0])
        for eng, rus in self.table_names.items():
            if rus == rus_name:
                self.current_table = eng
                break

        self.current_filters = ""
        self.current_sort = ""
        self.load_table_data()
        self.update_search_columns()

        self.status_bar.config(text=f"Таблица: {rus_name}")


    def update_search_columns(self):
        if not self.current_table:
            return

        columns_data = self.db.get_table_columns(self.current_table)
        if not columns_data:
            return

        self.search_column["values"] = [
            self.get_russian_column_name(col[0]) for col in columns_data
        ]

    def load_table_data(self, where_clause="", order_clause=""):
        if not self.current_table:
            return

        columns_data = self.db.get_table_columns(self.current_table)
        if not columns_data:
            return

        columns = [col[0] for col in columns_data]
        rus_columns = [self.get_russian_column_name(c) for c in columns]

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for i, col in enumerate(columns):
            self.tree.heading(col, text=rus_columns[i])
            self.tree.column(col, width=130)

        query = f"SELECT * FROM {self.current_table} {where_clause} {order_clause}"
        self.current_data = self.db.execute_query(query)

        for row in self.current_data:
            self.tree.insert("", END, values=row)

        self.status_bar.config(text=f"Записей: {len(self.current_data)}")


    def add_record(self):
        if not self.current_table:
            messagebox.showwarning("Ошибка", "Выберите таблицу")
            return
        self.open_edit_dialog()

    def edit_record(self):
        if not self.current_table:
            messagebox.showwarning("Ошибка", "Выберите таблицу")
            return

        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Ошибка", "Выберите запись")
            return

        values = self.tree.item(sel[0], "values")
        self.open_edit_dialog(values)

    def open_edit_dialog(self, values=None):
        dialog = EditDialog(self.root, self.db, self.current_table, values, self.column_names)
        self.root.wait_window(dialog.dialog)

        if dialog.saved:
            self.load_table_data(self.current_filters, self.current_sort)

    def delete_record(self):
        if not self.current_table:
            return

        sel = self.tree.selection()
        if not sel:
            return

        if not messagebox.askyesno("Подтверждение", "Удалить запись?"):
            return

        item = sel[0]
        values = self.tree.item(item, "values")

        columns = self.db.get_table_columns(self.current_table)
        pk = columns[0][0]

        query = f"DELETE FROM {self.current_table} WHERE {pk} = %s"
        self.db.execute_query(query, (values[0],))

        self.load_table_data(self.current_filters, self.current_sort)


    def search_records(self):
        if not self.current_table:
            return

        rus_column = self.search_column.get()
        value = self.search_value.get()

        column_eng = None
        for eng, rus in self.column_names.items():
            if rus == rus_column:
                column_eng = eng
                break

        if not column_eng: return

        self.current_filters = f"WHERE {column_eng}::text LIKE '%{value}%'"
        self.load_table_data(self.current_filters, self.current_sort)

    def clear_search(self):
        self.search_value.delete(0, END)
        self.current_filters = ""
        self.load_table_data()

    def open_filter_dialog(self):
        if not self.current_table:
            return

        dialog = FilterSortDialog(self.root, self.db, self.current_table, self.column_names)
        self.root.wait_window(dialog.dialog)

        where = f"WHERE {' AND '.join(dialog.filters)}" if dialog.filters else ""
        sort = f"ORDER BY {dialog.sort_column} {dialog.sort_direction}" if dialog.sort_column else ""

        self.current_filters = where
        self.current_sort = sort
        self.load_table_data(where, sort)

    def reset_view(self):
        self.current_filters = ""
        self.current_sort = ""
        self.search_value.delete(0, END)
        self.load_table_data()


    def open_route_transit_form(self):
        RouteTransitForm(self.root, self.db, self.column_names)

    def report_routes_by_destination(self):
        ReportDialog(self.root, self.db, "routes_by_destination", self.column_names)

    def report_upcoming_flights(self):
        ReportDialog(self.root, self.db, "upcoming_flights", self.column_names)

    def report_airlines_fleet(self):
        ReportDialog(self.root, self.db, "airlines_fleet", self.column_names)


if __name__ == "__main__":
    root = tk.Tk()
    style = Style(theme="flatly")
    app = AirportApp(root)
    root.mainloop()
