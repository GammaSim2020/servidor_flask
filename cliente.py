import os
import requests
from requests.auth import HTTPBasicAuth

API_URL    = os.getenv("API_URL", "http://127.0.0.1:5000")  # cambia a tu URL de Render cuando despliegues
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin123")

def get_privado():
    url = f"{API_URL}/api/datos"   # endpoint protegido en tu app
    r = requests.get(url, auth=HTTPBasicAuth(ADMIN_USER, ADMIN_PASS), timeout=10)
    r.raise_for_status()
    return r.json()

def add_item(nombre: str, stock: int):
    url = f"{API_URL}/api/items"
    payload = {"nombre": nombre, "stock": stock}
    r = requests.post(url, json=payload, auth=HTTPBasicAuth(ADMIN_USER, ADMIN_PASS), timeout=10)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    try:
        print("== GET /api/datos ==")
        print(get_privado())

        print("\n== POST /api/items ==")
        nuevo = add_item("Jander", 1000)
        print("Creado:", nuevo)

        print("\n== GET /api/datos (después) ==")
        print(get_privado())
    except requests.HTTPError as e:
        print("HTTPError:", e)
        if e.response is not None:
            print("Body:", e.response.text)
    except requests.RequestException as e:
        print("RequestException:", e)
