import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox


class EditDialog:
    def __init__(self, parent, db, table, values=None, column_names=None):
        self.db = db
        self.table = table
        self.values = values
        self.is_edit = values is not None
        self.column_names = column_names or {}
        self.saved = False

        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("✏️ Редактирование" if self.is_edit else "➕ Добавление")
        self.dialog.geometry("700x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Центрируем диалог
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (700 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (650 // 2)
        self.dialog.geometry(f"700x650+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        title = ttk.Label(
            main_frame,
            text="✏️ Редактирование записи" if self.is_edit else "➕ Добавление новой записи",
            font=("Segoe UI", 12, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 20))

        form_frame = ttk.Labelframe(main_frame, text="📝 Данные записи", bootstyle="info")
        form_frame.pack(fill=BOTH, expand=True, pady=(0, 20))

        canvas = tk.Canvas(form_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient=VERTICAL, command=canvas.yview, bootstyle="primary-round")
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        columns = self.db.get_table_columns(self.table)
        self.entries = {}
        row_index = 0

        for i, col in enumerate(columns):
            column_name = col[0]
            data_type = col[1].lower() if len(col) > 1 else ''

            if not self.is_edit and ('serial' in data_type or column_name == 'flight_time'):
                continue

            if self.table == 'routes' and column_name == 'flight_time':
                continue

            column_label = self.column_names.get(column_name, column_name)
            label = ttk.Label(self.scrollable_frame, text=column_label + ":", font=("Segoe UI", 10))
            label.grid(row=row_index, column=0, sticky=W, pady=8, padx=(10, 5))

            if column_name in ['departure_time', 'arrival_time'] and self.table in ['routes', 'transit_routes']:
                entry = ttk.Entry(self.scrollable_frame, width=30, font=("Segoe UI", 9))
                self.create_tooltip(entry, "Формат: YYYY-MM-DD HH:MM:SS+HH")

                if self.is_edit and i < len(self.values):
                    entry.insert(0, str(self.values[i]))
                else:
                    entry.insert(0, "2024-01-01 12:00:00+03")

            elif self.table in ['aircrafts', 'staff', 'routes', 'transit_routes'] and column_name in [
                'airport_code', 'airline_code', 'position_id', 'crew_id', 'service_id',
                'departure_airport', 'arrival_airport', 'base_airport', 'aircraft_code',
                'route_code', 'stop_airport'
            ]:
                entry = ttk.Combobox(self.scrollable_frame, font=("Segoe UI", 9))

                if 'airport' in column_name:
                    airports = self.db.get_airports()
                    entry['values'] = [f"{code} - {name}" for code, name in airports]
                elif 'airline' in column_name:
                    airlines = self.db.get_airlines()
                    entry['values'] = [f"{code} - {name}" for code, name in airlines]
                elif 'aircraft' in column_name:
                    aircrafts = self.db.get_aircrafts()
                    entry['values'] = [f"{code} - {name}" for code, name in aircrafts]
                elif 'position' in column_name:
                    positions = self.db.get_positions()
                    entry['values'] = [f"{id} - {name}" for id, name in positions]
                elif 'crew' in column_name:
                    crews = self.db.get_crews()
                    entry['values'] = [f"{id} - {name}" for id, name in crews]
                elif 'service' in column_name:
                    services = self.db.get_services()
                    entry['values'] = [f"{id} - {name}" for id, name in services]
                elif column_name == 'route_code':
                    routes = self.db.get_routes()
                    entry['values'] = [f"{code}" for code, in routes]

                entry.grid(row=row_index, column=1, sticky=W + E, pady=8, padx=(0, 10))

                if self.is_edit and i < len(self.values):
                    current_value = str(self.values[i])
                    for val in entry['values']:
                        if val.startswith(current_value):
                            entry.set(val)
                            break
                    else:
                        entry.insert(0, current_value)
            else:
                entry = ttk.Entry(self.scrollable_frame, width=30, font=("Segoe UI", 9))
                entry.grid(row=row_index, column=1, sticky=W + E, pady=8, padx=(0, 10))

                if self.is_edit and i < len(self.values):
                    entry.insert(0, str(self.values[i]))

            self.entries[column_name] = entry
            row_index += 1

        self.scrollable_frame.grid_columnconfigure(1, weight=1)

        canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=RIGHT, fill=Y, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="💾 Сохранить",
            command=self.save,
            bootstyle="success"
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="❌ Отмена",
            command=self.dialog.destroy,
            bootstyle="secondary"
        ).pack(side=LEFT)

    def create_tooltip(self, widget, text):

        def show_tooltip(event):
            tooltip = ttk.Toplevel(self.dialog)
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

    def save(self):
        try:
            columns = []
            values = []

            for col_name, entry in self.entries.items():
                if not self.is_edit:
                    column_info = self.db.get_table_columns(self.table)
                    for col_info in column_info:
                        if col_info[0] == col_name:
                            data_type = col_info[1].lower() if len(col_info) > 1 else ''
                            if 'serial' in data_type or (self.table == 'routes' and col_name == 'flight_time'):
                                continue

                value = entry.get().strip()

                if not value:
                    if not self.is_edit:
                        continue
                    else:
                        Messagebox.show_warning(
                            f"Заполните поле: {self.column_names.get(col_name, col_name)}",
                            "Предупреждение",
                            parent=self.dialog
                        )
                        return

                if isinstance(entry, ttk.Combobox) and ' - ' in str(value):
                    value = value.split(' - ')[0]

                columns.append(col_name)
                values.append(value)

            if self.is_edit:
                pk_column = list(self.entries.keys())[0]
                pk_value = self.values[0]

                set_clause = ", ".join([f"{col} = %s" for col in columns])
                query = f"UPDATE {self.table} SET {set_clause} WHERE {pk_column} = %s"
                result = self.db.execute_query(query, tuple(values + [pk_value]))
            else:
                placeholders = ", ".join(["%s"] * len(columns))
                columns_str = ", ".join(columns)
                query = f"INSERT INTO {self.table} ({columns_str}) VALUES ({placeholders})"
                result = self.db.execute_query(query, tuple(values))

            if result is not None:
                Messagebox.show_info("Данные успешно сохранены!", "✅ Успех", parent=self.dialog)
                self.saved = True
                self.dialog.destroy()
            else:
                Messagebox.show_error("Не удалось сохранить данные", "❌ Ошибка", parent=self.dialog)

        except Exception as e:
            Messagebox.show_error(f"Ошибка сохранения: {str(e)}", "❌ Ошибка", parent=self.dialog)