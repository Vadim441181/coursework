import psycopg2


class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host="192.168.56.101",
                port="5432",
                database="airport",
                user="postgres",
                password="postgres"
            )
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения: {e}")

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            return None

    def execute_query_with_return(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                self.connection.commit()
                return result
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            return None

    def get_table_columns(self, table_name):
        query = """
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """
        return self.execute_query(query, (table_name,))

    def get_airports(self):
        return self.execute_query("SELECT airport_code, airport_name FROM airports ORDER BY airport_name")

    def get_airlines(self):
        return self.execute_query("SELECT airline_code, airline_name FROM airlines ORDER BY airline_name")

    def get_aircrafts(self):
        return self.execute_query("SELECT aircraft_code, aircraft_name FROM aircrafts ORDER BY aircraft_name")

    def get_positions(self):
        return self.execute_query("SELECT position_id, position_name FROM positions ORDER BY position_name")

    def get_crews(self):
        return self.execute_query("SELECT crew_id, crew_name FROM crews ORDER BY crew_name")

    def get_services(self):
        return self.execute_query("SELECT service_id, service_name FROM services ORDER BY service_name")

    def get_routes(self):
        return self.execute_query("SELECT route_code FROM routes ORDER BY route_code")

    def close(self):
        if self.connection:
            self.connection.close()