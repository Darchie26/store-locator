# need to call starbucks API
import requests

#needed to parse through text returned by starbucks
import re

# we need to pull all of my data in a csv at the end
import pandas as pd

# fancy map
import folium

# check to see whether a start bucks in charlotte
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import json


# open zip code file
f = open('cltZips.txt', 'r')
cltZips = [z.replace('\n','') for z in f.readlines()]

allStores = []

for idx,z in enumerate(cltZips):

    # call request for 100 stores with current zipcode

    r = requests.get('https://www.starbucks.com/store-locator?place='+z)

    # if any response fails you will quit immediately
    if r.status_code != 200: raise SystemExit

    # process the text response that starbucks give back
    storeInfoList = processResponse(r.text)

    # truncate the returned zip code to a 5 digit zip
    for storeInfo in storeInfoList:
        storeInfo[6] = storeInfo[6][:5]

        #add store to a master list
        allStores += storeInfoList

seenStoreIds = []

cltStores = []

for store in allStores:
    # if We already seen this store id
    if store[0] in seenStoreIds:
        continue

    #if this is the first time seeing this store id,
    # then add it to cltStores and add its id to seenStoresIds

    else:
        cltStores.append(store)
        seenStoreIds.append(store[0])

# open up the Clt Geojson
with open ('cltMap.json') as f:
    cltArea = json.load(f)

    # convert the MultiPolygon part of the LA Geojson into a shapely Polygon object for easier inclusiveness checking
    cltPolygon = Polygon(cltArea['features'][0]['geometry']['coordinates'][0][0])
    
    # keep store if and only if it is within Clt polygon
    keepCltStores = []
    for store in cltStores:
        #geojson needs (long, lat) format instead of (lat, long)
        #convert the (long, lat) pair into a shapely Point object
        point = Point(float(store[3]), float (store[2]))
        if cltPolygon.contains(point):
            keepCltStores.append(store)
    
    