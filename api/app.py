from fastapi import FastAPI
from api.predict import predict

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "alive"}

@app.post("/predict")
def predict_price(data:dict):

    prediction = predict(data)

    return {
        "prediction": prediction,
        "status_code": 200
    }
