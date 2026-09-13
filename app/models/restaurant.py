from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cuisine = Column(String)
    address = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Float, default=0.0)

    owner = relationship("User")