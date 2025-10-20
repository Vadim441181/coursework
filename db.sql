-- Таблица: аэропорты
CREATE TABLE airports (
    airport_code CHAR(3) PRIMARY KEY,
    airport_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'Russia',
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    timezone TEXT NOT NULL
);

--Таблица: авиакомпании
CREATE TABLE airlines (
    airline_code CHAR(2) PRIMARY KEY,
    airline_name TEXT NOT NULL UNIQUE
);

-- Таблица: самолёты
CREATE TABLE aircrafts (
    aircraft_code CHAR(3) PRIMARY KEY,
    airport_code CHAR(3) NOT NULL,
    airline_code CHAR(2) NOT NULL,
    aircraft_name TEXT NOT NULL,
    capacity INT CHECK (capacity > 0),
    range_km INT CHECK (range_km > 0),
    FOREIGN KEY (airport_code)
        REFERENCES airports(airport_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (airline_code)
        REFERENCES airlines(airline_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Таблица: должности
CREATE TABLE positions (
    position_id SERIAL PRIMARY KEY,
    position_name TEXT UNIQUE NOT NULL
);

-- Таблица: экипажи
CREATE TABLE crews (
    crew_id SERIAL PRIMARY KEY,
    crew_name TEXT NOT NULL UNIQUE
);

-- Таблица: службы
CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    service_name TEXT UNIQUE NOT NULL
);

-- Таблица: персонал
CREATE TABLE staff (
    inn CHAR(12) PRIMARY KEY,
    full_name TEXT NOT NULL,
    airport_code CHAR(3) NOT NULL,
    position_id INT NOT NULL,
    crew_id INT,
    service_id INT,
    FOREIGN KEY (position_id) REFERENCES positions(position_id) ON DELETE SET NULL,
    FOREIGN KEY (crew_id) REFERENCES crews(crew_id) ON DELETE SET NULL,
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE SET NULL,
    FOREIGN KEY (airport_code) REFERENCES airports(airport_code) ON DELETE CASCADE
);

-- Таблица: маршруты
CREATE TABLE routes (
    route_code SERIAL PRIMARY KEY,
    departure_airport CHAR(3) NOT NULL,
    arrival_airport CHAR(3) NOT NULL,
    base_airport CHAR(3) NOT NULL,
    aircraft_code CHAR(3) NOT NULL,
    departure_time TIMESTAMPTZ NOT NULL,
    arrival_time TIMESTAMPTZ NOT NULL,
    flight_hours INT CHECK (flight_hours > 0),
    FOREIGN KEY (departure_airport) REFERENCES airports(airport_code),
    FOREIGN KEY (arrival_airport) REFERENCES airports(airport_code),
    FOREIGN KEY (base_airport) REFERENCES airports(airport_code),
    FOREIGN KEY (aircraft_code) REFERENCES aircrafts(aircraft_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (arrival_time > departure_time)
);

-- Таблица: транзитные маршруты
CREATE TABLE transit_routes (
    route_code INT NOT NULL,
    stop_num INT NOT NULL,
    stop_airport CHAR(3) NOT NULL,
    arrival_time TIMESTAMPTZ NOT NULL,
    departure_time TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (route_code, stop_num),
    FOREIGN KEY (route_code) REFERENCES routes(route_code)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (stop_airport) REFERENCES airports(airport_code),
    CHECK (arrival_time < departure_time)
);


--индекс для поиска всех аэропортов по стране
CREATE INDEX idx_airports_country ON airports(country);

--индекс для поиска самолётов по авиакомпании
CREATE INDEX idx_aircrafts_airline ON aircrafts(airline_code);

--индекс для поиска сотрудников по аэропорту  должности
CREATE INDEX idx_staff_airport_position ON staff(airport_code, position_id);


--базовая информация об аэропортах
CREATE VIEW airports_info AS
SELECT airport_name, city, country
FROM airports 
ORDER BY airport_name;


--данные о самолётах вместе с авиакомпанией и аэропортом базирования
CREATE VIEW aircrafts_info AS
SELECT a.aircraft_name, a.aircraft_code, a.capacity, a.range_km, al.airline_name, ap.airport_name AS base_airport
FROM aircrafts a 
JOIN airlines al ON a.airline_code = al.airline_code
JOIN airports ap ON a.airport_code = ap.airport_code
ORDER BY a.aircraft_name;


--подсчёт количества самолётов каждой авиакомпании и вывод только тех, у которых их больше 1

CREATE VIEW airlines_fleet AS
SELECT al.airline_name, COUNT(a.aircraft_code) AS aircraft_count
FROM airlines al
JOIN aircrafts a ON al.airline_code = a.airline_code
GROUP BY al.airline_name
HAVING COUNT(a.aircraft_code) > 1;


-- Функция для автоматического пересчёта часов полёта
CREATE OR REPLACE FUNCTION calc_flight_hours()
RETURNS TRIGGER AS $$
BEGIN
    NEW.flight_hours := EXTRACT(EPOCH FROM (NEW.arrival_time - NEW.departure_time)) / 3600;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calc_flight_hours
BEFORE INSERT OR UPDATE ON routes
FOR EACH ROW
EXECUTE FUNCTION calc_flight_hours();
