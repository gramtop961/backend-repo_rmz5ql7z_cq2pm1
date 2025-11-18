"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in currency units")
    category: str = Field(..., description="Category: dryfruits | spices | combos | gifting")
    image_url: Optional[str] = Field(None, description="Image URL")
    in_stock: bool = Field(True, description="Whether product is in stock")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Product ID as string")
    title: str = Field(..., description="Product title snapshot")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    price: float = Field(..., ge=0, description="Unit price at time of order")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    customer_name: str = Field(...)
    customer_email: str = Field(...)
    customer_phone: Optional[str] = Field(None)
    shipping_address: str = Field(...)
    items: List[OrderItem] = Field(...)
    subtotal: float = Field(..., ge=0)
    tax: float = Field(0.0, ge=0)
    total: float = Field(..., ge=0)

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
