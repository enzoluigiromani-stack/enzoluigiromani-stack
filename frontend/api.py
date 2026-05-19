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


# ── Activities ────────────────────────────────────────────────────────────────

def get_activities(token: str, page: int = 1, limit: int = 10) -> dict:
    try:
        res = requests.get(f"{API_URL}/activities",
                           params={"page": page, "limit": limit},
                           headers=_headers(token), timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return {"items": [], "total": 0, "page": 1, "limit": limit, "pages": 1}


def get_lead_timeline(lead_id: int, token: str, page: int = 1, limit: int = 50) -> dict:
    try:
        res = requests.get(f"{API_URL}/leads/{lead_id}/timeline",
                           params={"page": page, "limit": limit},
                           headers=_headers(token), timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return {"items": [], "total": 0, "page": 1, "limit": limit, "pages": 1}


# ── Tasks ─────────────────────────────────────────────────────────────────────

def get_tasks(token: str, status: str = None, priority: str = None,
              due_today: bool = False, overdue_only: bool = False,
              page: int = 1, limit: int = 50) -> dict:
    params = {"page": page, "limit": limit}
    if status:        params["status"] = status
    if priority:      params["priority"] = priority
    if due_today:     params["due_today"] = "true"
    if overdue_only:  params["overdue_only"] = "true"
    try:
        res = requests.get(f"{API_URL}/tasks/", params=params,
                           headers=_headers(token), timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return {"items": [], "total": 0, "page": 1, "limit": limit, "pages": 1}


def create_task(data: dict, token: str) -> dict:
    res = requests.post(f"{API_URL}/tasks/", json=data,
                        headers=_headers(token), timeout=5)
    res.raise_for_status()
    return res.json()


def complete_task(task_id: int, token: str) -> dict:
    res = requests.patch(f"{API_URL}/tasks/{task_id}/complete",
                         headers=_headers(token), timeout=5)
    res.raise_for_status()
    return res.json()


def refresh_tasks(token: str) -> dict:
    try:
        res = requests.post(f"{API_URL}/tasks/refresh",
                            headers=_headers(token), timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception:
        return {}


def move_lead(lead_id: int, stage_id: int, token: str) -> dict:
    res = requests.patch(
        f"{API_URL}/leads/{lead_id}/move",
        json={"stage_id": stage_id},
        headers=_headers(token),
        timeout=5,
    )
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
