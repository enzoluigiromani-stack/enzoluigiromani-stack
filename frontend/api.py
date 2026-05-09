import requests

API_URL = "http://localhost:8000"


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Auth ──────────────────────────────────────────────────────────────────────

def register(name: str, email: str, password: str) -> dict:
    res = requests.post(f"{API_URL}/auth/register",
                        json={"name": name, "email": email, "password": password}, timeout=5)
    res.raise_for_status()
    return res.json()


def login(email: str, password: str) -> dict:
    res = requests.post(f"{API_URL}/auth/login",
                        json={"email": email, "password": password}, timeout=5)
    res.raise_for_status()
    return res.json()


def get_me(token: str) -> dict:
    res = requests.get(f"{API_URL}/auth/me", headers=_headers(token), timeout=5)
    res.raise_for_status()
    return res.json()


# ── Workspace ─────────────────────────────────────────────────────────────────

def get_workspace(token: str) -> dict:
    res = requests.get(f"{API_URL}/workspace/me", headers=_headers(token), timeout=5)
    res.raise_for_status()
    return res.json()


def get_workspace_settings(token: str) -> dict:
    res = requests.get(f"{API_URL}/workspace/settings", headers=_headers(token), timeout=5)
    res.raise_for_status()
    return res.json()


def update_workspace_settings(data: dict, token: str) -> dict:
    res = requests.put(f"{API_URL}/workspace/settings", json=data,
                       headers=_headers(token), timeout=5)
    res.raise_for_status()
    return res.json()


# ── Leads ─────────────────────────────────────────────────────────────────────

def get_leads(token: str) -> list:
    try:
        res = requests.get(f"{API_URL}/leads/", headers=_headers(token), timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return []


def create_lead(data: dict, token: str) -> dict:
    res = requests.post(f"{API_URL}/leads/", json=data, headers=_headers(token), timeout=5)
    res.raise_for_status()
    return res.json()


# ── Pipeline ──────────────────────────────────────────────────────────────────

def get_board(token: str) -> list:
    try:
        res = requests.get(f"{API_URL}/pipeline/board", headers=_headers(token), timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return []
