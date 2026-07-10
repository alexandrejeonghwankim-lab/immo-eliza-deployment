# Immo-eliza-deployment

This repository contains the deployment part of the Immo Eliza property price prediction project.

The goal is to expose a trained machine learning model through a FastAPI backend, provide a user-friendly Streamlit frontend, and connect both deployed services together.

## Repository Structure

```
immo-eliza-deployment/
|
|-- api/
|   |-- app.py              # FastAPI application and API endpoints
|   |-- predict.py          # Loads the trained model and returns predictions
|   |-- preprocessing.py    # Cleans input data and creates model features
|   |-- config.py           # Feature column configuration used by the model
|   |-- pipeline.py         # Pipeline-related code for model/data processing
|   |-- train_xgboost.py    # Training script for the XGBoost model
|   |-- test_predict.py     # Local tests for prediction logic
|   |-- __init__.py         # Marks api as a Python package
|
|-- data/
|   |-- postal_code_coordinates.csv  # Postal code lookup used for coordinates
|
|-- model/
|   |-- model_xgboost2.pkl           # Saved XGBoost model artifact used for API prediction
|   
|
|-- streamlit/
|   |-- streamlit_app.py    # Streamlit frontend application
|
|-- image/
|   |-- Immo_Eliza_proper                 # Images used by the Streamlit app or documentation
|   |-- Immo_Eliza  
|
|-- Dockerfile              # Docker configuration for deploying the FastAPI backend
|-- requirements.txt        # Python dependencies for API and Streamlit
|-- README.md               # Main project documentation
```

## What this Repository Contains

1. A FastAPI backend that exposes the machine learning model through API endpoints.
2. A Streamlit frontend that allows users to enter property information and receive a predicted price.
3. A combined deployment setup where the Streamlit app calls the deployed FastAPI API.

The final user flow is:

```text
User fills in property information in Streamlit
        |
        v
Streamlit sends the data as JSON to FastAPI
        |
        v
FastAPI preprocesses the data and calls the ML model
        |
        v
The model returns a predicted price
        |
        v
Streamlit displays the predicted price to the user
```

## 1. FastAPI Backend

### Purpose

The FastAPI backend is responsible for exposing the property price prediction model through HTTP endpoints. This allows other applications, such as Streamlit, to send property information and receive a prediction in JSON format.

The backend is useful because it separates the machine learning logic from the user interface. Developers or other services can call the API without needing to understand the Streamlit frontend.

### Main Files


```
api/app.py
api/predict.py
api/preprocessing.py
api/config.py
model/model_xgboost2.pkl
Dockerfile
requirements.txt
```

### How it works?



1. `api/app.py` defines the FastAPI application.
2. The `/` route checks whether the API is alive.
3. The `/predict` route receives property data as JSON.
4. FastAPI validates the data using a Pydantic model.
5. The validated data is passed to `predict()` in `api/predict.py`.
6. `predict.py` loads the trained model and runs preprocessing.
7. `preprocessing.py` cleans the data and creates the feature columns expected by the model.
8. The model returns a predicted property price.
9. FastAPI sends the prediction back as JSON.


### API Endpoints



```text
GET /
```

Purpose: health check endpoint.

Example response:

```json
{
  "status": "alive"
}
```

```text
POST /predict
```

Purpose: receives property information and returns a predicted price.

Example response:

```json
{
  "prediction": 337012.53,
  "status_code": 200
}
```

### Deployment


The FastAPI backend is deployed on Render using Docker.

The deployed API URL is:

```text
https://immo-eliza-deployment-ru4g.onrender.com/
```

The prediction endpoint is:

```text
https://immo-eliza-deployment-ru4g.onrender.com/predict
```

Because the project uses Render's free tier, the API can sleep after inactivity. The first request after sleeping may take longer.

## 2. Streamlit Frontend

### Purpose

The Streamlit frontend provides a user-friendly interface for non-technical users. Instead of sending JSON manually to the API, users can fill in a form with property information and click a button to receive the predicted price.

This part is focused on usability. It makes the model accessible to people who do not write code.


### Main File

```text
streamlit/streamlit_app.py
```

### What The Streamlit App Does

The Streamlit app collects:

- Property type
- Livable surface
- Optional total land surface
- Number of bedrooms
- Number of bathrooms
- Number of toilets
- Province
- Postal code
- Optional address
- Optional latitude and longitude
- EPC score
- Kitchen equipment
- Optional property features such as garden, terrace, swimming pool, solar panels, and more

### User Flow

1. The user opens the Streamlit app.
2. The user fills in the property information.
3. The app validates required fields, such as livable surface and postal code.
4. If an address is provided, the app tries to convert it into latitude and longitude using Nominatim.
5. The app creates a JSON dictionary called `property_data`.
6. The app sends `property_data` to the deployed FastAPI `/predict` endpoint.
7. The app receives the prediction.
8. The predicted price is displayed in a readable format, for example:

```text
Predicted price: 337,012.53 EUR
```



### Streamlit Design Choices

The Streamlit app uses a clear form layout with sections:

```text
Property Information
Location Information
Energy and Equipment
Optional Information
Prediction
```

The app also includes:

- Postal code validation
- EPC options based on the selected province
- Optional address geocoding
- A spinner to wake up the deployed API
- Error messages for invalid input or API timeout
- An expander that shows the request data sent to the API

## 3. Combined Deployment: FastAPI + Streamlit

### Purpose

The final goal is to combine both deployed parts:


```text
FastAPI = backend / prediction service
Streamlit = frontend / user interface
```

This is the full Option 3 architecture.

### Final Architecture

```text
User
 |
 v
Streamlit app
 |
 v
FastAPI API deployed on Render
 |
 v
Preprocessing + XGBoost model
 |
 v
Prediction response
 |
 v
Streamlit displays the predicted price
```

### How Both Parts Are Connected

In `streamlit/streamlit_app.py`, the API URL points to the deployed Render endpoint:

```python
API_URL = "https://immo-eliza-deployment-ru4g.onrender.com/predict"
```

When the user clicks the prediction button, Streamlit sends a POST request:

```python
response = requests.post(API_URL, json=property_data, timeout=90)
```

The API returns a prediction, and Streamlit displays it.

### Deployment Steps

#### FastAPI on Render

1. Create a Dockerfile for the API.
2. Push the repository to GitHub.
3. Create a Render Web Service.
4. Select Docker as the runtime.
5. Connect Render to the GitHub repository.
6. Deploy the API.
7. Test the `/` and `/predict` endpoints.

#### Streamlit on Streamlit Community Cloud

1. Push `streamlit/streamlit_app.py` and `requirements.txt` to GitHub.
2. Create a new Streamlit Community Cloud app.
3. Select the GitHub repository.
4. Set the main file path:

```text
streamlit/streamlit_app.py
```

5. Deploy the app.
6. Test the full flow from Streamlit to FastAPI.

### Important Notes

- Render free services may sleep after inactivity.
- The first prediction can take longer because the API may need to wake up.
- The Streamlit app includes a wake-up request to reduce confusion for users.
- If the API timeout happens, the user can wait and try again.



## Installation For Local Development

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the FastAPI app locally:

```powershell
uvicorn api.app:app --reload
```

Run the Streamlit app locally:

```powershell
streamlit run streamlit/streamlit_app.py
```

## Technologies Used

- Python
- FastAPI
- Pydantic
- Pandas
- Scikit-learn
- XGBoost
- Joblib
- Streamlit
- Requests
- Docker
- Render
- Streamlit Community Cloud

## Project Status

The project includes:

- A deployed FastAPI backend
- A deployed Streamlit frontend
- A connected full prediction workflow
- API speed improvements by loading the model once
- Optional address geocoding
- User input validation

## Future Improvements

Possible next improvements:

- Improve the visual design of the Streamlit app
- Add more detailed API error messages
- Add automated tests for the API endpoint
- Improve model performance with more training data
- Replace free Render hosting with a non-sleeping service for faster response time
- Add a more detailed README with screenshots and live demo links

`![Immo Eliza banner](image/Immo_Eliza.png)`
