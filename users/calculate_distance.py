import geopy

''' function dis() takes in two coordinates to calculate the distance in kilometers between them'''

def dis(coord_1,coord_2):
    distance=geopy.distance.distance(coord_1, coord_2).km
    return distance
