from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import products, orders, users, auth

# Creates tables automatically if they don't exist yet — fine for early
# development. Once you have real data, switch to Alembic migrations
# instead of relying on this.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grocery Delivery App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your real frontend domain before going live
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(users.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Grocery delivery API is running"}
