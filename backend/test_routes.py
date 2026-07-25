from app.api.v1.auth.router import router
for r in router.routes:
    print(r.path, r.methods)
