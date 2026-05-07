import requests

API_URL = "http://localhost:8001"


def get_leads() -> list:
    try:
        res = requests.get(f"{API_URL}/leads/", timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return []


def get_board() -> list:
    try:
        res = requests.get(f"{API_URL}/pipeline/board", timeout=5)
        res.raise_for_status()
        return res.json().get("board", [])
    except Exception:
        return []


def create_lead(data: dict) -> dict:
    res = requests.post(f"{API_URL}/leads/", json=data, timeout=5)
    res.raise_for_status()
    return res.json()
