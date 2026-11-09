from sqlalchemy import Column, String, Numeric, Boolean, JSON, ForeignKey
from app.models.base import TimeStampedModel

class Product(TimeStampedModel):
    __tablename__ = "products"
    
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)
    rating = Column(Numeric(3, 2), default=4.5, nullable=False)
    image_url = Column(String(500), nullable=True)
    meta_info = Column(JSON, default=dict)

