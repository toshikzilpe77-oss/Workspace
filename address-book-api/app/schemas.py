from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class AddressBase(BaseModel):
   
    name: str = Field(..., description="A descriptive name or title for the location.")
    street: str
    city: str
    
    # Geospatial coordinates with strict validation to ensure they are valid
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate, must be between -90 and 90.")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate, must be between -180 and 180.")

# --- Input Schemas ---

class AddressCreate(AddressBase):
   
    pass


class Address(AddressBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class AddressWithDistance(Address):
    distance_km: float = Field(..., description="The calculated geodesic distance from the query point to this address, in kilometers.")