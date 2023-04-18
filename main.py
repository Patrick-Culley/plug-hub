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
    req = requests.get(f'https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={config.stations_key}&fuel_type=E85,ELEC&location={data}&limit=100').json() 
    req = req['fuel_stations']

    return render_template('search.html', raw=json.dumps(req), locale=location, data=req)   


if __name__ == "__main__":
    app.run(threaded=True)