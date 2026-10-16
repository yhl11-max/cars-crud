import os
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app import database, mysql_database
from app.schemas import CarInput

DB_PATH = Path(os.environ.get("CARS_DB_PATH", Path(__file__).resolve().parent.parent / "cars.db"))

# Tests passing a SQLite file path always keep using SQLite.
storage = mysql_database if os.getenv("CARS_DB_BACKEND") == "mysql" else database

app = FastAPI(title="Cars CRUD")
storage.initialize(DB_PATH)


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------
@app.post("/api/cars", status_code=201)
def api_create_car(car: CarInput):
    saved = storage.create_car(DB_PATH, car)
    body = (
        f'{{"id": {saved.id}, "make": "{saved.make}", '
        f'"model": "{saved.model}", "year": {saved.year}, "color": "{saved.color}"}}'
    )
    return Response(
        content=body,
        media_type="application/json",
        status_code=201,
        headers={"Location": f"/api/cars/{saved.id}"},
    )


@app.get("/api/cars")
def api_list_cars():
    return storage.list_cars(DB_PATH)


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------
def _page(body: str) -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Cars</title>"
        "<link rel='stylesheet' href='/static/style.css'></head>"
        f"<body>{body}</body></html>"
    )


@app.get("/", response_class=HTMLResponse)
def index():
    cars = storage.list_cars(DB_PATH)
    rows = "".join(
        f'<li><a href="/cars/{c.id}">{c.make} {c.model} ({c.year})</a></li>'
        for c in cars
    )
    return _page(
        f"<h1>Cars</h1><ul>{rows}</ul><p><a href='/cars/new'>Add a car</a></p>"
    )


@app.get("/cars/new", response_class=HTMLResponse)
def new_car_page():
    return _page(
        """<h1>Add a car</h1>
<form method="post" action="/cars/new">
  <p><label for="make">Make</label> <input id="make" name="make"></p>
  <p><label for="model">Model</label> <input id="model" name="model"></p>
  <p><label for="year">Year</label> <input id="year" name="year"></p>
  <p><label for="color">Color</label> <input id="color" name="color"></p>
  <p><button type="submit">Create car</button></p>
</form>"""
    )


@app.post("/cars/new")
def create_car_submit(
    make: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    color: str = Form(...),
):
    car = CarInput(make=make, model=model, year=year, color=color)
    saved = storage.create_car(DB_PATH, car)
    return RedirectResponse(url=f"/cars/{saved.id}", status_code=303)


@app.get("/cars/{car_id}", response_class=HTMLResponse)
def car_detail(car_id: int):
    car = storage.get_car(DB_PATH, car_id)
    if car is None:
        return _page("<h1>Not found</h1>")
    return _page(
        f"""<h1>{car.make} {car.model}</h1>
<dl>
  <dt>Make</dt><dd id="car-make">{car.make}</dd>
  <dt>Model</dt><dd id="car-model">{car.model}</dd>
  <dt>Year</dt><dd id="car-year">{car.year}</dd>
  <dt>Color</dt><dd id="car-color">{car.color}</dd>
</dl>
<p><a href="/cars/{car.id}/edit">Edit car</a></p>
<p><a href="/">Back to list</a></p>"""
    )


@app.get("/cars/{car_id}/edit", response_class=HTMLResponse)
def edit_car_page(car_id: int):
    car = storage.get_car(DB_PATH, car_id)
    if car is None:
        return _page("<h1>Not found</h1>")
    return _page(
        f"""<h1>Edit {car.make} {car.model}</h1>
<form method="post" action="/cars/{car.id}/edit">
  <p><label for="make">Make</label> <input id="make" name="make" value="{car.make}"></p>
  <p><label for="model">Model</label> <input id="model" name="model" value="{car.model}"></p>
  <p><label for="year">Year</label> <input id="year" name="year" value="{car.year}"></p>
  <p><label for="color">Color</label> <input id="color" name="color" value="{car.color}"></p>
  <p><button type="submit">Save changes</button></p>
</form>"""
    )


@app.post("/cars/{car_id}/edit")
def update_car_submit(
    car_id: int,
    make: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    color: str = Form(...),
):
    car = CarInput(make=make, model=model, year=year, color=color)
    storage.update_car(DB_PATH, car_id, car)
    return RedirectResponse(url=f"/cars/{car_id}", status_code=303)
