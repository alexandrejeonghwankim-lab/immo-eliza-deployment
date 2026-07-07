from predict import predict

sample ={
   
    "livable_surface": 120,
    "total_land_surface": 300,
    "bedrooms": 3,
    "bathrooms": 1,
    "toilets": 2
 
}


result = predict(sample)

print(result)
