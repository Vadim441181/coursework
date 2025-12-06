import tkinter as tk
from tkinter import ttk, messagebox


class ReportDialog:

    def __init__(self, parent, db, report_type, column_names=None):
        self.db = db
        self.report_type = report_type
        self.column_names = column_names or {}
        self.report_data = []

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(self.get_report_title())
        self.dialog.geometry("900x600")

        self.create_widgets()

    def get_report_title(self):
        titles = {
            "routes_by_destination": "Маршруты по пункту назначения",
            "upcoming_flights": "Ближайшие рейсы",
            "airlines_fleet": "Флот авиакомпаний"
        }
        return titles.get(self.report_type, "Отчет")

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        params_frame = ttk.LabelFrame(main_frame, text="Параметры отчета")
        params_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_report_params(params_frame)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="Сформировать отчет",
                   command=self.generate_report).pack(side=tk.LEFT, padx=(0, 5))

        self.tree = ttk.Treeview(main_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_bar = ttk.Label(main_frame, text="Выберите параметры и нажмите 'Сформировать отчет'")
        self.status_bar.pack(fill=tk.X, pady=(5, 0))

    def create_report_params(self, parent):
        if self.report_type == "routes_by_destination":
            ttk.Label(parent, text="Аэропорт назначения:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            self.destination_combo = ttk.Combobox(parent)
            airports = self.db.get_airports()
            self.destination_combo['values'] = [f"{code} - {name}" for code, name in airports]
            self.destination_combo.grid(row=0, column=1, sticky=tk.W + tk.E, padx=5, pady=2)

            ttk.Label(parent, text="Сортировка:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            self.sort_combo = ttk.Combobox(parent, values=["Время вылета", "Время прибытия", "Время полета"])
            self.sort_combo.grid(row=1, column=1, sticky=tk.W + tk.E, padx=5, pady=2)
            self.sort_combo.set("Время вылета")

        elif self.report_type == "upcoming_flights":
            ttk.Label(parent, text="Период (часы):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            self.hours_entry = ttk.Entry(parent)
            self.hours_entry.insert(0, "24")
            self.hours_entry.grid(row=0, column=1, sticky=tk.W + tk.E, padx=5, pady=2)

            ttk.Label(parent, text="Авиакомпания:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            self.airline_combo = ttk.Combobox(parent)
            airlines = self.db.get_airlines()
            self.airline_combo['values'] = ["Все"] + [f"{code} - {name}" for code, name in airlines]
            self.airline_combo.grid(row=1, column=1, sticky=tk.W + tk.E, padx=5, pady=2)
            self.airline_combo.set("Все")

        elif self.report_type == "airlines_fleet":
            ttk.Label(parent, text="Минимальное кол-во самолетов:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            self.min_aircrafts = ttk.Entry(parent)
            self.min_aircrafts.insert(0, "1")
            self.min_aircrafts.grid(row=0, column=1, sticky=tk.W + tk.E, padx=5, pady=2)

            ttk.Label(parent, text="Сортировка:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            self.sort_combo = ttk.Combobox(parent,
                                           values=["По кол-ву самолетов", "По общей вместимости", "По авиакомпании"])
            self.sort_combo.grid(row=1, column=1, sticky=tk.W + tk.E, padx=5, pady=2)
            self.sort_combo.set("По кол-ву самолетов")

    def generate_report(self):
        try:
            if self.report_type == "routes_by_destination":
                self.generate_routes_report()
            elif self.report_type == "upcoming_flights":
                self.generate_upcoming_flights_report()
            elif self.report_type == "airlines_fleet":
                self.generate_airlines_fleet_report()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка формирования отчета: {e}")

    def generate_routes_report(self):
        destination = self.destination_combo.get()
        if not destination:
            messagebox.showwarning("Предупреждение", "Выберите аэропорт назначения")
            return

        destination_code = destination.split(' - ')[0]
        sort_option = self.sort_combo.get()

        sort_map = {
            "Время вылета": "r.departure_time",
            "Время прибытия": "r.arrival_time",
            "Время полета": "r.flight_time"
        }
        sort_field = sort_map.get(sort_option, "r.departure_time")

        query = f"""
            SELECT r.route_code, 
                   dep.airport_name as departure_airport,
                   arr.airport_name as arrival_airport,
                   r.departure_time,
                   r.arrival_time,
                   r.flight_time,
                   a.aircraft_name,
                   al.airline_name,
                   COUNT(tr.stop_num) as transit_stops
            FROM routes r
            JOIN airports dep ON r.departure_airport = dep.airport_code
            JOIN airports arr ON r.arrival_airport = arr.airport_code
            JOIN aircrafts a ON r.aircraft_code = a.aircraft_code
            JOIN airlines al ON a.airline_code = al.airline_code
            LEFT JOIN transit_routes tr ON r.route_code = tr.route_code
            WHERE r.arrival_airport = %s
            GROUP BY r.route_code, dep.airport_name, arr.airport_name, a.aircraft_name, al.airline_name, r.flight_time
            ORDER BY {sort_field}
        """

        results = self.db.execute_query(query, (destination_code,))

        russian_columns = ["Код", "Аэропорт вылета", "Аэропорт назначения", "Время вылета",
                           "Время прибытия", "Время полета", "Самолет", "Авиакомпания", "Остановки"]

        self.display_report(russian_columns, results)

        total_routes = len(results)
        self.status_bar.config(text=f"Найдено маршрутов: {total_routes}")

    def generate_upcoming_flights_report(self):
        hours = int(self.hours_entry.get())
        airline = self.airline_combo.get()

        airline_filter = ""
        if airline != "Все":
            airline_code = airline.split(' - ')[0]
            airline_filter = f"AND al.airline_code = '{airline_code}'"

        query = f"""
            SELECT r.route_code,
                   dep.airport_name as departure_airport,
                   arr.airport_name as arrival_airport,
                   r.departure_time,
                   r.arrival_time,
                   al.airline_name,
                   a.aircraft_name,
                   r.flight_time
            FROM routes r
            JOIN airports dep ON r.departure_airport = dep.airport_code
            JOIN airports arr ON r.arrival_airport = arr.airport_code
            JOIN aircrafts ac ON r.aircraft_code = ac.aircraft_code
            JOIN airlines al ON ac.airline_code = al.airline_code
            JOIN aircrafts a ON r.aircraft_code = a.aircraft_code
            WHERE r.departure_time BETWEEN NOW() AND NOW() + INTERVAL '{hours} hours'
            {airline_filter}
            ORDER BY r.departure_time
        """

        results = self.db.execute_query(query)

        russian_columns = ["Код", "Аэропорт вылета", "Аэропорт назначения", "Время вылета",
                           "Время прибытия", "Авиакомпания", "Самолет", "Время полета"]

        self.display_report(russian_columns, results)

        self.status_bar.config(text=f"Ближайшие рейсы ({hours} часов): {len(results)} рейсов")

    def generate_airlines_fleet_report(self):
        min_aircrafts = int(self.min_aircrafts.get())
        sort_option = self.sort_combo.get()

        sort_map = {
            "По кол-ву самолетов": "aircraft_count DESC",
            "По общей вместимости": "total_capacity DESC",
            "По авиакомпании": "al.airline_name"
        }
        sort_field = sort_map.get(sort_option, "aircraft_count DESC")

        query = f"""
            SELECT al.airline_name,
                   COUNT(a.aircraft_code) as aircraft_count,
                   SUM(a.capacity) as total_capacity,
                   AVG(a.range_km) as avg_range,
                   MAX(a.range_km) as max_range,
                   MIN(a.capacity) as min_capacity,
                   STRING_AGG(a.aircraft_name, ', ') as aircraft_list
            FROM airlines al
            LEFT JOIN aircrafts a ON al.airline_code = a.airline_code
            GROUP BY al.airline_name
            HAVING COUNT(a.aircraft_code) >= %s
            ORDER BY {sort_field}
        """

        results = self.db.execute_query(query, (min_aircrafts,))

        russian_columns = ["Авиакомпания", "Кол-во самолетов", "Общая вместимость", "Средняя дальность",
                           "Макс. дальность", "Мин. вместимость", "Список самолетов"]

        self.display_report(russian_columns, results)

        total_aircrafts = sum(row[1] for row in results)
        total_capacity = sum(row[2] for row in results if row[2])
        self.status_bar.config(
            text=f"Авиакомпаний: {len(results)} | Самолетов: {total_aircrafts} | Общая вместимость: {total_capacity}")

    def display_report(self, columns, data):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        if data:
            for row in data:
                self.tree.insert("", tk.END, values=row)
            self.report_data = data
        else:
            self.report_data = []