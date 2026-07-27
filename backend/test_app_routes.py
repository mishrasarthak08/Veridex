from app.main import app

def test_routes():
    for r in app.routes:
        if hasattr(r, "path"):
            print(r.path, getattr(r, "name", "unnamed"))
