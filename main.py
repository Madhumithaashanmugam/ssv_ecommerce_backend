from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import configure_mappers
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import os
import logging

# Routers
from api.vendor.user import user_router as vendor_user_router
from api.customer.user import auth_router as otp_router, user_router as customer_user_router
from api.vendor.auth import auth_router as vendor_auth_router
from api.customer.auth import auth_router as login_router
from api.vendor.category import category_router
from api.vendor.items import item_router
from api.vendor.analytics import analytics_router
from api.dependency import get_current_vendor, get_current_customer

# from api.vendor.order_items import order_items_router
from api.customer.cart import cart_router
from api.customer.order import order_router
from api.customer.address import address_router
from api.customer.guest_user import guest_user_router
from api.vendor.offline_orders import offline_router

# Create uploads folder if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Load .env variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Create FastAPI app
app = FastAPI(
    title="E-Commerce Backend",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# ✅ CORS Middleware (early in the app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Configure mappers
configure_mappers()

# ✅ Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ Include routers
app.include_router(vendor_user_router, prefix="/api/vendor/users", tags=["Vendor Users"])
app.include_router(vendor_auth_router, prefix="/api/vendor/auth", tags=["Vendor Auth"])
app.include_router(category_router, prefix="/categories")
app.include_router(analytics_router, prefix="/analytics")
app.include_router(item_router, prefix="/items")
app.include_router(offline_router, prefix="/offline-order", tags=["Offline Order"])
# app.include_router(order_items_router, prefix="/order-items")

app.include_router(otp_router, prefix="/api/customer/auth/otp", tags=["Customer OTP"])
app.include_router(customer_user_router, prefix="/api/customer/users", tags=["Customer Users"])
app.include_router(login_router, prefix="/api/customer/auth", tags=["Customer Auth"])
app.include_router(cart_router, prefix="/cart", tags=["Cart"])
app.include_router(address_router, prefix="/address", tags=["Address"])
app.include_router(guest_user_router, prefix="/guest-user", tags=["Guest User"])
app.include_router(order_router)


# ✅ Main entrypoint
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
