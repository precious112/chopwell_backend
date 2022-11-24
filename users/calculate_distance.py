from geopy.distance import geodesic

''' function dis() takes in two coordinates to calculate the distance in kilometers between them'''

def dis(coord_1,coord_2):
    distance=geodesic(coord_1, coord_2).km
    return distance

def convert_to_float(num):
    return float(num)
