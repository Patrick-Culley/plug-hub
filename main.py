import json
from flask import Flask, request, render_template
from geopy.geocoders import Nominatim
import config 
import requests, googlemaps, geocoder, geopy

# Constructor takes (name) of module as arg 
app = Flask(__name__)

# Obtain Coordinates of current user location 
gmaps = googlemaps.Client(key=f'{config.gkey}')
my_location = geocoder.ip('me').latlng

@app.route('/', methods=['GET'])
def index():
    lat_long = {'lat': [],'long': []}
    # Fetch nearest stations based on current coordinates 
    if request.method == "GET":
        req = requests.get(f'https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={config.stations_key}&fuel_type=E85,ELEC&latitude={my_location[0]}&longitude={my_location[1]}&limit=200').json()
        data = req['fuel_stations']
        length = len(req)

        # Obtain station latitude/longitude 
        for el in range(len(data)): 
            lat_long['lat'].append(data[el]['latitude'])
            lat_long['long'].append(data[el]['longitude'])
        llen = len(lat_long['long'])

    return render_template('base.html', data=data, raw=json.dumps(data),
                           length=length, gkey = config.gkey,
                           my_location=my_location, lat_long=lat_long, llen=llen)


@app.route('/search', methods=['GET'])
def search(): 
    return render_template('search.html')


if __name__ == "__main__":
    app.run(threaded=True)