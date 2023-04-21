import json, time, asyncio
from flask import Flask, request, render_template, redirect, url_for, session
from geopy.geocoders import Nominatim
import config 
import requests, googlemaps, geocoder

# Constructor takes (name) of module as arg 
app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

# Obtain Coordinates of current user location 
gmaps = googlemaps.Client(key=f'{config.gkey}')
my_location = geocoder.ip('me').latlng

# ROUTES 
@app.route('/', methods=['GET', 'POST'])
def index():
    lat_long = {'lat': [],'long': []}
    # Fetch nearest stations based on local coordinates 
    req = requests.get(f'https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={config.stations_key}&fuel_type=E85,ELEC&latitude={my_location[0]}&longitude={my_location[1]}&limit=200').json()
    data = req['fuel_stations']
    length = len(req)
    
    if request.method == 'POST': 
        session['request'] = request.form.get('text')
        return redirect(url_for('search'))
    
    return render_template('base.html', data=data, raw=json.dumps(data),
                        length=length, gkey = config.gkey,
                        my_location=my_location, lat_long=lat_long)


@app.route('/search', methods=['GET', 'POST'])
def search():  
    if(request.args.get('result')):
        data = request.args.get('result')
    else:
        data = session['request']
    # Obtain lat and long from search input    
    location = geocoder.google(data, key=config.gkey).latlng
    req = requests.get(f'https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={config.stations_key}&fuel_type=E85,ELEC&location={data}&limit=200').json() 
    req = req['fuel_stations']

    return render_template('search.html', raw=json.dumps(req), locale=location, data=req)   


@app.route('/directions', methods=['POST', 'GET'])
def directions(): 
    latlng = []
    coords = []
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    querystring = {"waypoints":"37.804829,-122.272476|37.871593,-122.272743","mode":"drive"}

    headers = {
        "X-RapidAPI-Key": config.rapid_api_key,
        "X-RapidAPI-Host": "route-and-directions.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    res = response.json()
    route = res['features'][0]['geometry']['coordinates'][0]
    print(route)
    for el in route:
        coords.append({'lat': el[1], 'lng': el[0]})
    print(coords)
    req = requests.get(f'https://maps.googleapis.com/maps/api/directions/json?destination=Montreal&origin=Toronto&key=AIzaSyAzJJ6fNaERr3gzPlQQoCFlolR_jX0jjkY').json()
    coordinates = req['routes'][0]['legs'][0]['steps']

    for el in range(len(coordinates)): 
        latlng.append(coordinates[el]['end_location'])

    return render_template('directions.html', route=json.dumps(coords))


if __name__ == "__main__":
    app.run(threaded=True)