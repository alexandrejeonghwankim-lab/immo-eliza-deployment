from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from api.predict import predict


app = FastAPI()

class PropertyInput(BaseModel):
    livable_surface: float
    bedrooms: int
    bathrooms: int
    toilets: int
    category: str
    province: str
    postal_code: str

    total_land_surface: Optional[float] = None
    terrace_orientation: Optional[str] = "unknown"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    epc: Optional[str] = None
    kitchen_equipment: Optional[str] = None

    garden: Optional[bool] = False
    terrace: Optional[bool] = False
    swimming_pool: Optional[bool] = False
    fireplace: Optional[bool] = False
    solar_panels: Optional[bool] = False
    air_conditioning: Optional[bool] = False
    vat: Optional[bool] = False
    electrical_certificate: Optional[bool] = False
    security_door: Optional[bool] = False
    hammam_sauna_jacuzzi: Optional[bool] = False

@app.get("/")
def health_check():
    return {"status": "alive"}

@app.post("/predict")
def predict_price(data: PropertyInput):
    prediction = predict(data.model_dump(exclude_none=True))

    return {
        "prediction": prediction,
        "status_code": 200
    }
