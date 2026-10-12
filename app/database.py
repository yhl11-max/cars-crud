import sqlite3
from typing import Optional, List

from app.schemas import CarInput


class Outcome(dict):
    """Dict that also exposes keys as attributes (saved.id, saved.make ...)."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


def _connect(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def initialize(db_path) -> None:
    conn = _connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            color TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def create_car(db_path, car: CarInput) -> Outcome:
    conn = _connect(db_path)
    cur = conn.execute(
        "INSERT INTO cars (make, model, year, color) VALUES (?, ?, ?, ?)",
        (car.make, car.model, car.year, car.color),
    )
    conn.commit()
    car_id = cur.lastrowid
    conn.close()
    return get_car(db_path, car_id)


def get_car(db_path, car_id: int) -> Optional[Outcome]:
    conn = _connect(db_path)
    row = conn.execute("SELECT * FROM cars WHERE id = ?", (car_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return Outcome(dict(row))


def list_cars(db_path) -> List[Outcome]:
    conn = _connect(db_path)
    rows = conn.execute("SELECT * FROM cars ORDER BY id").fetchall()
    conn.close()
    return [Outcome(dict(r)) for r in rows]


def delete_car(db_path, car_id: int) -> None:
    conn = _connect(db_path)
    conn.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    conn.commit()
    conn.close()


def update_car(db_path, car_id: int, car: CarInput) -> Optional[Outcome]:
    conn = _connect(db_path)
    conn.execute(
        "UPDATE cars SET make = ?, model = ?, year = ?, color = ? WHERE id = ?",
        (car.make, car.model, car.year, car.color, car_id),
    )
    conn.commit()
    conn.close()
    return get_car(db_path, car_id)
