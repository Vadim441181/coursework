import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox


class RouteTransitForm:

    def __init__(self, parent, db, column_names=None):
        self.db = db
        self.column_names = column_names or {}
        self.transit_data = []

        self.form_window = ttk.Toplevel(parent)
        self.form_window.title("✈️ Добавление маршрута с транзитными остановками")
        self.form_window.geometry("1100x750")
        self.form_window.transient(parent)
        self.form_window.grab_set()

        self.form_window.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (1100 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (750 // 2)
        self.form_window.geometry(f"1100x750+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        main_container = ttk.Frame(self.form_window)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        left_column = ttk.Frame(main_container)
        left_column.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        right_column = ttk.Frame(main_container, width=180)
        right_column.pack(side=RIGHT, fill=Y, padx=(10, 0))
        right_column.pack_propagate(False)

        header_frame = ttk.Frame(left_column)
        header_frame.pack(fill=X, pady=(0, 15))

        title = ttk.Label(
            header_frame,
            text="✈️ Добавление нового маршрута с остановками",
            font=("Segoe UI", 12, "bold"),
            bootstyle="primary"
        )
        title.pack()

        scrollable_container = ttk.Frame(left_column)
        scrollable_container.pack(fill=BOTH, expand=True)

        canvas = tk.Canvas(scrollable_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scrollable_container, orient=VERTICAL, command=canvas.yview,
                                  bootstyle="primary-round")
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        route_frame = ttk.Labelframe(scrollable_frame, text="📝 Основные данные маршрута", bootstyle="info")
        route_frame.pack(fill=X, pady=(0, 15), padx=5)

        route_inner = ttk.Frame(route_frame)
        route_inner.pack(padx=10, pady=10, fill=X)

        airports = self.db.get_airports()
        aircrafts = self.db.get_aircrafts()

        airport_values = [f"{code} - {name}" for code, name in airports]
        aircraft_values = [f"{code} - {name}" for code, name in aircrafts]

        row = 0
        ttk.Label(route_inner, text="Аэропорт вылета:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=W, pady=8)
        self.departure_combo = ttk.Combobox(route_inner, values=airport_values, font=("Segoe UI", 9), width=35)
        self.departure_combo.grid(row=row, column=1, sticky=W + E, padx=10, pady=8)

        row += 1
        ttk.Label(route_inner, text="Аэропорт назначения:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=W, pady=8)
        self.arrival_combo = ttk.Combobox(route_inner, values=airport_values, font=("Segoe UI", 9), width=35)
        self.arrival_combo.grid(row=row, column=1, sticky=W + E, padx=10, pady=8)

        row += 1
        ttk.Label(route_inner, text="Базовый аэропорт:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=W, pady=8)
        self.base_combo = ttk.Combobox(route_inner, values=airport_values, font=("Segoe UI", 9), width=35)
        self.base_combo.grid(row=row, column=1, sticky=W + E, padx=10, pady=8)

        row += 1
        ttk.Label(route_inner, text="Самолет:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=W, pady=8)
        self.aircraft_combo = ttk.Combobox(route_inner, values=aircraft_values, font=("Segoe UI", 9), width=35)
        self.aircraft_combo.grid(row=row, column=1, sticky=W + E, padx=10, pady=8)

        row += 1
        ttk.Label(route_inner, text="Время вылета:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=W, pady=8)
        self.departure_time = ttk.Entry(route_inner, font=("Segoe UI", 9), width=35)
        self.departure_time.grid(row=row, column=1, sticky=W + E, padx=10, pady=8)
        self.departure_time.insert(0, "2024-01-01 12:00:00+03")
        self.create_tooltip(self.departure_time, "Формат: YYYY-MM-DD HH:MM:SS+HH (например: 2024-01-01 14:30:00+03)")

        row += 1
        ttk.Label(route_inner, text="Время прибытия:", font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky=W, pady=8)
        self.arrival_time = ttk.Entry(route_inner, font=("Segoe UI", 9), width=35)
        self.arrival_time.grid(row=row, column=1, sticky=W + E, padx=10, pady=8)
        self.arrival_time.insert(0, "2024-01-01 15:30:00+03")
        self.create_tooltip(self.arrival_time, "Формат: YYYY-MM-DD HH:MM:SS+HH (например: 2024-01-01 16:30:00+03)")

        route_inner.grid_columnconfigure(1, weight=1)

        transit_frame = ttk.Labelframe(scrollable_frame, text="🛬 Транзитные остановки", bootstyle="warning")
        transit_frame.pack(fill=BOTH, expand=True, pady=15, padx=5)

        transit_buttons = ttk.Frame(transit_frame)
        transit_buttons.pack(fill=X, padx=10, pady=10)

        ttk.Button(
            transit_buttons,
            text="➕ Добавить остановку",
            command=self.add_transit_stop,
            bootstyle="success-outline"
        ).pack(side=LEFT, padx=(0, 5))

        ttk.Button(
            transit_buttons,
            text="🗑️ Удалить остановку",
            command=self.delete_transit_stop,
            bootstyle="danger-outline"
        ).pack(side=LEFT)

        columns = ("stop_num", "airport", "arrival_time", "departure_time")
        self.transit_tree = ttk.Treeview(
            transit_frame,
            columns=columns,
            show="headings",
            height=8,
            bootstyle="primary"
        )

        self.transit_tree.heading("stop_num", text="№ Остановки")
        self.transit_tree.heading("airport", text="Аэропорт")
        self.transit_tree.heading("arrival_time", text="Время прибытия")
        self.transit_tree.heading("departure_time", text="Время вылета")

        self.transit_tree.column("stop_num", width=80)
        self.transit_tree.column("airport", width=180)
        self.transit_tree.column("arrival_time", width=170)
        self.transit_tree.column("departure_time", width=170)

        self.transit_tree.tag_configure('oddrow', background='#f8f9fa')
        self.transit_tree.tag_configure('evenrow', background='white')

        tree_scrollbar = ttk.Scrollbar(transit_frame, orient=VERTICAL, command=self.transit_tree.yview,
                                       bootstyle="primary-round")
        self.transit_tree.configure(yscrollcommand=tree_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(transit_frame, orient=HORIZONTAL, command=self.transit_tree.xview,
                                    bootstyle="primary-round")
        self.transit_tree.configure(xscrollcommand=h_scrollbar.set)

        self.transit_tree.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=(0, 5))
        h_scrollbar.pack(side=BOTTOM, fill=X, padx=10)
        tree_scrollbar.pack(side=RIGHT, fill=Y, pady=10)


        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)


        actions_label = ttk.Label(
            right_column,
            text="⚡ Действия",
            font=("Segoe UI", 11, "bold"),
            bootstyle="primary"
        )
        actions_label.pack(pady=(0, 20))

        actions_frame = ttk.Frame(right_column)
        actions_frame.pack(fill=BOTH, expand=True)


        save_btn = ttk.Button(
            actions_frame,
            text="Сохранить\nмаршрут",
            command=self.save_route,
            bootstyle="success",
            width=15,
            padding=15
        )
        save_btn.pack(pady=(0, 20))

        cancel_btn = ttk.Button(
            actions_frame,
            text="❌ Отмена",
            command=self.form_window.destroy,
            bootstyle="secondary",
            width=15
        )
        cancel_btn.pack(pady=10)

        info_frame = ttk.Labelframe(right_column, text="📊 Информация", bootstyle="light")
        info_frame.pack(fill=X, pady=(30, 0))

        info_inner = ttk.Frame(info_frame)
        info_inner.pack(padx=10, pady=10)

        self.stop_count_label = ttk.Label(
            info_inner,
            text="Остановок: 0",
            font=("Segoe UI", 9)
        )
        self.stop_count_label.pack(anchor=W)


    def create_tooltip(self, widget, text):

        def show_tooltip(event):
            tooltip = ttk.Toplevel(self.form_window)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = ttk.Label(tooltip, text=text, bootstyle="inverse-dark", padding=5)
            label.pack()

            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def add_transit_stop(self):
        stop_window = ttk.Toplevel(self.form_window)
        stop_window.title("➕ Добавление транзитной остановки")
        stop_window.geometry("550x450")
        stop_window.transient(self.form_window)
        stop_window.grab_set()

        stop_window.update_idletasks()
        x = self.form_window.winfo_rootx() + (self.form_window.winfo_width() // 2) - (550 // 2)
        y = self.form_window.winfo_rooty() + (self.form_window.winfo_height() // 2) - (450 // 2)
        stop_window.geometry(f"550x450+{x}+{y}")

        main_frame = ttk.Frame(stop_window, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        ttk.Label(
            main_frame,
            text="➕ Добавление транзитной остановки",
            font=("Segoe UI", 11, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 20))

        ttk.Label(main_frame, text="Номер остановки:", font=("Segoe UI", 10)).pack(anchor=W, pady=5)
        stop_num = ttk.Entry(main_frame, font=("Segoe UI", 9))
        stop_num.pack(fill=X, pady=(0, 10))

        ttk.Label(main_frame, text="Аэропорт:", font=("Segoe UI", 10)).pack(anchor=W, pady=5)
        airport_combo = ttk.Combobox(main_frame, font=("Segoe UI", 9))
        airports = self.db.get_airports()
        airport_combo['values'] = [f"{code} - {name}" for code, name in airports]
        airport_combo.pack(fill=X, pady=(0, 10))

        ttk.Label(main_frame, text="Время прибытия:", font=("Segoe UI", 10)).pack(anchor=W, pady=5)
        arrival_time = ttk.Entry(main_frame, font=("Segoe UI", 9))
        arrival_time.pack(fill=X, pady=(0, 10))
        arrival_time.insert(0, "2024-01-01 13:00:00+03")
        self.create_tooltip(arrival_time, "Формат: YYYY-MM-DD HH:MM:SS+HH")

        ttk.Label(main_frame, text="Время вылета:", font=("Segoe UI", 10)).pack(anchor=W, pady=5)
        departure_time = ttk.Entry(main_frame, font=("Segoe UI", 9))
        departure_time.pack(fill=X, pady=(0, 20))
        departure_time.insert(0, "2024-01-01 13:30:00+03")
        self.create_tooltip(departure_time, "Формат: YYYY-MM-DD HH:MM:SS+HH")

        def save_stop():
            try:
                stop_num_val = stop_num.get().strip()
                airport_val = airport_combo.get()

                if not all([stop_num_val, airport_val]):
                    Messagebox.show_warning(
                        "Заполните номер остановки и выберите аэропорт",
                        "⚠️ Предупреждение",
                        parent=stop_window
                    )
                    return

                if ' - ' not in airport_val:
                    Messagebox.show_warning(
                        "Выберите аэропорт из списка",
                        "⚠️ Предупреждение",
                        parent=stop_window
                    )
                    return

                arrival_val = arrival_time.get().strip()
                departure_val = departure_time.get().strip()

                stop_data = (
                    stop_num_val,
                    airport_val.split(' - ')[0],
                    arrival_val,
                    departure_val
                )

                item_id = self.transit_tree.insert("", tk.END, values=stop_data)
                tag = 'evenrow' if len(self.transit_tree.get_children()) % 2 == 0 else 'oddrow'
                self.transit_tree.item(item_id, tags=(tag,))

                self.transit_data.append(stop_data)
                stop_window.destroy()

                count = len(self.transit_tree.get_children())
                self.stop_count_label.config(text=f"Остановок: {count}")
            except Exception as e:
                Messagebox.show_error(
                    f"Ошибка добавления остановки: {str(e)}",
                    "❌ Ошибка",
                    parent=stop_window
                )

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=10)

        ttk.Button(
            button_frame,
            text="Добавить",
            command=save_stop,
            bootstyle="success"
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="Отмена",
            command=stop_window.destroy,
            bootstyle="secondary"
        ).pack(side=LEFT)

    def delete_transit_stop(self):
        selection = self.transit_tree.selection()
        if selection:
            for item in selection:
                self.transit_tree.delete(item)
            count = len(self.transit_tree.get_children())
            self.stop_count_label.config(text=f"Остановок: {count}")
        else:
            Messagebox.show_warning(
                "Выберите остановку для удаления",
                "⚠️ Предупреждение",
                parent=self.form_window
            )

    def save_route(self):
        try:
            departure_val = self.departure_combo.get()
            arrival_val = self.arrival_combo.get()
            base_val = self.base_combo.get()
            aircraft_val = self.aircraft_combo.get()

            if not all([departure_val, arrival_val, base_val, aircraft_val]):
                Messagebox.show_warning(
                    "Заполните все основные поля маршрута",
                    "⚠️ Предупреждение",
                    parent=self.form_window
                )
                return

            if ' - ' not in departure_val or ' - ' not in arrival_val or ' - ' not in base_val or ' - ' not in aircraft_val:
                Messagebox.show_warning(
                    "Выберите значения из списков",
                    "⚠️ Предупреждение",
                    parent=self.form_window
                )
                return

            departure_code = departure_val.split(' - ')[0]
            arrival_code = arrival_val.split(' - ')[0]
            base_code = base_val.split(' - ')[0]
            aircraft_code = aircraft_val.split(' - ')[0]

            departure_time_val = self.departure_time.get().strip()
            arrival_time_val = self.arrival_time.get().strip()

            query = """
                INSERT INTO routes (departure_airport, arrival_airport, base_airport, aircraft_code, departure_time, arrival_time)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING route_code
            """

            result = self.db.execute_query_with_return(query, (
                departure_code, arrival_code, base_code, aircraft_code,
                departure_time_val, arrival_time_val
            ))

            if result:
                route_code = result[0][0]

                transit_count = 0
                for item in self.transit_tree.get_children():
                    values = self.transit_tree.item(item, 'values')
                    if len(values) >= 4:
                        transit_query = """
                            INSERT INTO transit_routes (route_code, stop_num, stop_airport, arrival_time, departure_time)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        transit_result = self.db.execute_query(transit_query, (
                            route_code, values[0], values[1], values[2], values[3]
                        ))
                        if transit_result is not None:
                            transit_count += 1

                Messagebox.show_info(
                    f"Маршрут #{route_code} успешно сохранен с {transit_count} остановками",
                    "✅ Успех",
                    parent=self.form_window
                )
                self.form_window.destroy()
            else:
                Messagebox.show_error(
                    "Не удалось сохранить маршрут",
                    "❌ Ошибка",
                    parent=self.form_window
                )

        except Exception as e:
            Messagebox.show_error(
                f"Ошибка сохранения: {str(e)}",
                "❌ Ошибка",
                parent=self.form_window
            )