from fastapi import FastAPI
from mangum import Mangum
from app.api.products_routes import router as products_router

app = FastAPI(title="Products Service", version="1.0.0")

app.include_router(products_router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "products"}


handler = Mangum(app)
