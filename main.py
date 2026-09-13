from fastapi import FastAPI
from app.routers import auth, restaurants, menu,cart, address, order, review

app = FastAPI(title="Food Delivery Backend")

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(address.router)
app.include_router(order.router)
app.include_router(review.router)

@app.get("/")
def root():
    return {"message": "Food Delivery Backend is running"}