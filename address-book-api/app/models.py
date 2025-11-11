from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True, doc="Unique identifier for the address entry.")
    
    name = Column(String, index=True, doc="A user-friendly name or title for the location.")
    street = Column(String, doc="Street address details.")
    city = Column(String, doc="City of the address.")
    
    latitude = Column(Float, index=True, doc="Latitude coordinate (e.g., 34.0522).")
    longitude = Column(Float, index=True, doc="Longitude coordinate (e.g., -118.2437).")
    
    def __repr__(self):
        """Returns a string representation of the object."""
        return f"<Address(id={self.id}, name='{self.name}', coords=({self.latitude}, {self.longitude}))>"