import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order, OrderItem, User

app = FastAPI(title="Priyansh Dryfruits & Spices API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Priyansh Dryfruits & Spices Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

@app.get("/schema")
def get_schema():
    # Simple schema discovery for viewer tools
    return {
        "collections": ["user", "product", "order"],
        "models": {
            "user": User.model_json_schema(),
            "product": Product.model_json_schema(),
            "order": Order.model_json_schema(),
        }
    }

# Seed endpoint to insert initial products if empty
@app.post("/seed")
def seed_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    existing = db["product"].count_documents({})
    if existing > 0:
        return {"status": "ok", "message": "Products already seeded"}

    products = [
        {"title": "Premium Almonds", "description": "Handpicked Californian almonds.", "price": 699.0, "category": "dryfruits", "image_url": "/images/almonds.jpg", "in_stock": True},
        {"title": "Whole Cashews", "description": "Crisp and buttery cashews.", "price": 749.0, "category": "dryfruits", "image_url": "/images/cashews.jpg", "in_stock": True},
        {"title": "Pistachios", "description": "Roasted and lightly salted.", "price": 899.0, "category": "dryfruits", "image_url": "/images/pistachios.jpg", "in_stock": True},
        {"title": "Walnuts", "description": "Omega-3 rich walnut kernels.", "price": 799.0, "category": "dryfruits", "image_url": "/images/walnuts.jpg", "in_stock": True},
        {"title": "Raisins", "description": "Golden seedless raisins.", "price": 299.0, "category": "dryfruits", "image_url": "/images/raisins.jpg", "in_stock": True},
        {"title": "Cardamom (Elaichi)", "description": "Aromatic whole green cardamom.", "price": 459.0, "category": "spices", "image_url": "/images/cardamom.jpg", "in_stock": True},
        {"title": "Black Pepper", "description": "Bold Malabar black pepper.", "price": 349.0, "category": "spices", "image_url": "/images/blackpepper.jpg", "in_stock": True},
        {"title": "Turmeric Powder", "description": "Pure Lakadong turmeric.", "price": 199.0, "category": "spices", "image_url": "/images/turmeric.jpg", "in_stock": True},
        {"title": "Red Chilli Powder", "description": "Vibrant Byadgi chilli powder.", "price": 229.0, "category": "spices", "image_url": "/images/redchilli.jpg", "in_stock": True},
        {"title": "Spice Gift Box", "description": "Curated spice box for gifting.", "price": 1299.0, "category": "gifting", "image_url": "/images/spicebox.jpg", "in_stock": True},
        {"title": "Dry Fruits Combo", "description": "Assorted premium dry fruits.", "price": 1499.0, "category": "combos", "image_url": "/images/combobox.jpg", "in_stock": True},
    ]

    for p in products:
        create_document("product", Product(**p))

    return {"status": "ok", "inserted": len(products)}

# Public product list with optional category filter
@app.get("/products", response_model=List[Product])
def list_products(category: Optional[str] = None):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filter_q = {"category": category} if category else {}
    docs = get_documents("product", filter_q)
    # Convert ObjectId and timestamps to serializable
    result = []
    for d in docs:
        d.pop("_id", None)
        result.append(Product(**d))
    return result

class CheckoutRequest(BaseModel):
    customer_name: str
    customer_email: str
    shipping_address: str
    items: List[OrderItem]

@app.post("/checkout")
def checkout(payload: CheckoutRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in payload.items)
    tax = round(subtotal * 0.05, 2)
    total = round(subtotal + tax, 2)
    order = Order(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        shipping_address=payload.shipping_address,
        items=payload.items,
        subtotal=subtotal,
        tax=tax,
        total=total
    )
    order_id = create_document("order", order)
    return {"status": "success", "order_id": order_id, "total": total}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
