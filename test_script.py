import requests

payload = {
    "id_servidor": "test_server",
    "cpu": 10.0,
    "ram": 20.0,
    "temp": 30.0,
    "disk": 40.0,
    "usuarios": [{"nombre": "jules", "terminal": "pts/0", "inicio": "2024-03-09 10:00:00"}]
}

try:
    r = requests.post("http://127.0.0.1:8000/reportar", json=payload)
    print("Report:", r.status_code, r.text)

    r = requests.get("http://127.0.0.1:8000/estado")
    print("Estado:", r.status_code, r.text)
except Exception as e:
    print(e)
