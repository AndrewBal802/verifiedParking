import requests
import operator
import urllib
import json
import gmaps
import math
from ipywidgets.embed import embed_minimal_html

api_key = "AIzaSyC73GKEofVek8VaW8-U289mdJ0batdsk7w"
base_url= "https://maps.googleapis.com/maps/api/geocode/json?"

#takes a user input and return the tuple (lat, lng)
def LocationConvertion():
    user_location = input("Enter your location:\n")
    parameters = {"address": user_location,
                "key": api_key}
    #print(f"{base_url}{urllib.parse.urlencode(parameters)}")
    r = requests.get(f"{base_url}{urllib.parse.urlencode(parameters)}")
    data = json.loads(r.content)
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    #print(data)
    return(lat,lng)

#user is tuple (lat, lng)
#PLdatabase is a list of dictionaries {id, lat, lon, capacity, hourly_rate, reservation_type}
def BestFive(user, PLdatabase):
    distances = dict()
    R = 6373.0
    for record in PLdatabase:
        dlat = abs(record['lat'] - user[0])
        dlon = abs(record['lon'] - user[1])
        a = math.sin(dlat / 2)**2 + math.cos(record['lat']) * math.cos(user[0]) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        distances[record['_id']] = distance
    distances = sorted(distances.items(), key=operator.itemgetter(1))
    return distances[0:5]
    

#parking_lots is a list of the tuples (lat,lng) representing the best five parking lots
def Demo(parking_lots):
    gmaps.configure(api_key=api_key)
    fig = gmaps.figure()
    markers = gmaps.marker_layer(parking_lots)
    fig.add_layer(markers)
    embed_minimal_html('export.html', views=[fig])

def GetDirection(origin, destination):
    base_url = "https://www.google.com/maps/dir/?api=1"
    output = base_url + "&origin=" + origin.replace(" ", "+") + "&destination=" + destination.replace(" ", "+") + "&travelmode=driving"
    return output

