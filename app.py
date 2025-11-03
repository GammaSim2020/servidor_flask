# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from functools import wraps
from flask import Flask, jsonify, request, abort, Response
from werkzeug.security import generate_password_hash, check_password_hash

AUTH_MODE = os.getenv("AUTH_MODE", "basic").lower()  # "apikey" | "basic"
API_KEY = os.getenv("API_KEY", "mi-super-key")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

app = Flask(__name__)

# Ruta del archivo de datos JSON (puede venir incluido en el repo)
DATA_PATH = Path(__file__).with_name("data.json")

# --- Decorador de autenticacion ---
def protected(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # --- API KEY ---
        if AUTH_MODE == "apikey":
            key = request.headers.get("X-API-Key")
            if key != API_KEY:
                abort(401, description="API key invalida o ausente")
            return fn(*args, **kwargs)

        # --- BASIC AUTH ---
        elif AUTH_MODE == "basic":
            auth = request.authorization
            if not auth or auth.username != ADMIN_USER or not check_password_hash(generate_password_hash(ADMIN_PASS), auth.password):
                return Response(
                    "No autorizado",
                    401,
                    {"WWW-Authenticate": 'Basic realm="Login Required"'},
                )
            return fn(*args, **kwargs)

        else:
            abort(500, description="AUTH_MODE desconocido: {}".format(AUTH_MODE))

    return wrapper


# --- Rutas ---
@app.get("/")
def raiz():
    return "API OK (AUTH_MODE={})".format(AUTH_MODE)


@app.get("/salud")
def salud():
    return jsonify(ok=True)


@app.get("/api/datos")
@protected
def get_datos():
    if not DATA_PATH.exists():
        abort(404, description="data.json no encontrado")
    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.post("/api/items")
@protected
def add_item():
    if not DATA_PATH.exists():
        abort(404, description="data.json no encontrado")

    body = request.get_json(silent=True) or {}
    nombre = body.get("nombre")
    stock = body.get("stock")

    if not isinstance(nombre, str) or not isinstance(stock, int):
        abort(400, description="Formato inválido. Ejemplo: {'nombre':'Cámara','stock':5}")

    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    nuevo_id = max((i["id"] for i in data.get("items", [])), default=0) + 1
    nuevo_item = {"id": nuevo_id, "nombre": nombre, "stock": stock}
    data.setdefault("items", []).append(nuevo_item)

    with DATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify(nuevo_item), 201


# --- Ejecutar en modo local ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
