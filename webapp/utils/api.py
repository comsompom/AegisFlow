"""Call backend FastAPI from Flask webapp."""
import requests
from flask import current_app


def get_backend_url(path: str) -> str:
    base = current_app.config.get("BACKEND_API_URL", "http://localhost:8000")
    return f"{base.rstrip('/')}{path}"


def get(path: str, **kwargs):
    try:
        r = requests.get(get_backend_url(path), timeout=10, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": str(e), "status": getattr(e.response, "status_code", None)}


def post(path: str, json=None, **kwargs):
    try:
        r = requests.post(get_backend_url(path), json=json, timeout=10, **kwargs)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        resp = getattr(e, "response", None)
        if resp is not None:
            try:
                data = resp.json()
                if "detail" in data:
                    data["error"] = data["detail"] if isinstance(data["detail"], str) else str(data["detail"])
                return data
            except Exception:
                pass
            return {"error": str(e), "detail": resp.text}
        return {"error": str(e)}


def delete(path: str, json=None, **kwargs):
    try:
        r = requests.delete(get_backend_url(path), json=json, timeout=10, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}
    except requests.RequestException as e:
        return {"error": str(e)}
