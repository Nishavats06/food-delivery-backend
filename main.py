from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers import auth, restaurants, menu, cart, address, order, review, location

app = FastAPI(title="Food Delivery Backend")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0]
    field = first_error["loc"][-1]
    message = f"{field} is required or invalid"
    return JSONResponse(
        status_code=422,
        content={"status_code": 422, "message": message}
    )

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(address.router)
app.include_router(order.router)
app.include_router(review.router)
app.include_router(location.router)

@app.get("/")
def root():
    return {"message": "Food Delivery Backend is running"}


# from fastapi import FastAPI
# from app.routers import auth, restaurants, menu,cart, address, order, review

# app = FastAPI(title="Food Delivery Backend")

# app.include_router(auth.router)
# app.include_router(restaurants.router)
# app.include_router(menu.router)
# app.include_router(cart.router)
# app.include_router(address.router)
# app.include_router(order.router)
# app.include_router(review.router)

# @app.get("/")
# def root():
#     return {"message": "Food Delivery Backend is running"}