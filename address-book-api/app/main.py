from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geopy.distance import geodesic
import logging
from typing import List, Dict, Any
from . import models, schemas
from .database import engine, get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Geospatial Address Book API",
    description="A robust API for managing address coordinates and querying nearby locations using geospatial distance calculation.",
    version="1.0.0"
)

@app.post("/addresses/", 
          response_model=schemas.Address, 
          status_code=status.HTTP_201_CREATED)
def create_address_entry(address: schemas.AddressCreate, db: Session = Depends(get_db)):
   
    db_address = models.Address(**address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    logger.info(f"Created new address with ID: {db_address.id}")
    return db_address

@app.get("/addresses/{address_id}", 
         response_model=schemas.Address)
def get_address_entry(address_id: int, db: Session = Depends(get_db)):
   
    db_address = db.query(models.Address).filter(models.Address.id == address_id).first()
    
    if db_address is None:
        logger.warning(f"Attempted to read non-existent address ID: {address_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
        
    return db_address

@app.put("/addresses/{address_id}", 
        response_model=schemas.Address)
def update_address_entry(address_id: int, address: schemas.AddressCreate, db: Session = Depends(get_db)):
   
    db_address = db.query(models.Address).filter(models.Address.id == address_id).first()
    
    if db_address is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    update_data = address.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_address, key, value)
    
    db.commit()
    db.refresh(db_address)
    logger.info(f"Updated address ID: {address_id}")
    return db_address

@app.delete("/addresses/{address_id}", 
            status_code=status.HTTP_204_NO_CONTENT)
def delete_address_entry(address_id: int, db: Session = Depends(get_db)):
  
    db_address = db.query(models.Address).filter(models.Address.id == address_id).first()
    
    if db_address is None:
        return 

    db.delete(db_address)
    db.commit()
    logger.info(f"Deleted address ID: {address_id}")
    return 



@app.get("/addresses/nearby/", 
         response_model=List[schemas.AddressWithDistance])
def find_nearby_addresses(
    lat: float, 
    lon: float, 
    distance_km: float = 5.0, # Default 5 kilometers
    db: Session = Depends(get_db)
):
    
    if distance_km <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Search radius (distance_km) must be a positive number.")

    center_point = (lat, lon)
    
    all_addresses = db.query(models.Address).all()
    
    nearby_addresses: List[Dict[str, Any]] = []
    
    for address in all_addresses:
        address_point = (address.latitude, address.longitude)
        
        distance = geodesic(center_point, address_point).km
        
        if distance <= distance_km:
            address_data = schemas.Address.from_orm(address).dict()
            address_data['distance_km'] = round(distance, 2)
            nearby_addresses.append(address_data)
            
    if not nearby_addresses:
        logger.info(f"No addresses found near ({lat}, {lon}) within {distance_km} km.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No addresses found within {distance_km} km of the specified location."
        )
            
    return nearby_addresses