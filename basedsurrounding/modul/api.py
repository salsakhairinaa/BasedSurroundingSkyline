# Modul Pengumpulan Data

## Import Library
import requests 	# get data menggunakan URL
import json			# mengolah data hasil request yang berbentuk json
import pandas as pd # mengolah DataFrame
import math			# nanti dipakai ketika skyline
import time 		# delay request data

## API KEY
# API Key Google Maps didapatkan setelah registrasi sebagai Developer dan menggunakan FREE trial
# Free Trial diberikan selama setahun dengan credit $300
# https://cloud.google.com/maps.platform/
api_key =''

## API yang digunakan Placae API
# Place Search - Find Place requests - Mendapatkan informasi geometri suatu tempat
# https://developers.google.com/places/web-service/search#FindPlaceRequests
url_findplace 		= "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
# Place Search - Nearby Search requests - Mendapatkan objek disekitar lokasi target
# https://developers.google.com/places/web-service/search#PlaceSearchRequests
url_nearbysearch 	= 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'

# fungsi untuk mendapatkan longitude dan latitude lokasi target
def get_geometry_target(loc_target):
    req = url_findplace+'input='+loc_target+'&inputtype=textquery&fields=geometry&key='+api_key
    request = requests.get(req)
    hasil = json.loads(request.text)
    
    lat = str(hasil['candidates'][0]['geometry']['location']['lat'])
    lng = str(hasil['candidates'][0]['geometry']['location']['lng'])
    
    return lat, lng

# fungsi untuk filter informasi yang dibutuhkan
def data_bersih(places, list_places_awal):
	list_poi = places
	for poi in list_poi['results']:
		baris = []
		nama = poi['name']
		latitude, longitude = poi['geometry']['location']['lat'], poi['geometry']['location']['lng']
		rating = poi.get('rating',float('0'))
		baris.append(nama)
		baris.append(latitude)
		baris.append(longitude)
		baris.append(rating)
		list_places_awal.append(baris)
	return(list_places_awal)

# fungsi untuk mendapatkan objek sekitar lokasi target
def findPlaces(loc, rad, tipe, pagetoken = None):
	if pagetoken:
		request = url_nearbysearch+'pagetoken='+pagetoken+'&key='+api_key
	else:
		request = url_nearbysearch+'location='+loc+'&radius='+rad+'&type='+tipe+'&key='+api_key
	hasil = json.loads(requests.get(request).text)
	return hasil

# fungsi main untuk mendapatkan objek disekitar target
def get_object(loc, rad, tipe):
	list_places_awal=[]
	places_awal = findPlaces(loc, rad, tipe)
	data_bersih(places_awal, list_places_awal)
	while 'next_page_token' in places_awal:
		pagetoken = places_awal['next_page_token']
		places_awal = findPlaces(loc, rad, tipe, pagetoken)
		data_bersih(places_awal, list_places_awal)
		time.sleep(5)
	#list_awal = pd.DataFrame(list_places_awal)
	return list_places_awal

# fungsi untuk mendapatkan long lat object
def get_geo(list_geo_target):
    loc_2 = []
    for loc_poi in list_geo_target:
        pl=loc_poi[1:3]
        loc_q = str(pl[0])+','+str(pl[1])
        loc_2.append(loc_q)
    return loc_2

# fungsi untuk mendapatkan jumlah fasilitas sekitar objek
def get_sum_facilities(list_tipe_2, loc_2, rating_tempat, rad_2, list_places_awal):
    for poi_q in list_tipe_2:
        for loc_q in range(0, len(loc_2)):
            dt_poi_q = findPlaces(loc_2[loc_q], rad_2, poi_q)
            #jumlahnya = len(dt_poi_q['results'])
            jum = 0
            for sumnya in dt_poi_q['results']:
                if('rating' in sumnya):
                    if(float(sumnya['rating']) >= rating_tempat):
                        jum += 1
            while 'next_page_token' in dt_poi_q:
                pagetoken = dt_poi_q['next_page_token']
                time.sleep(5)
                dt_poi_q = findPlaces(loc_2[loc_q], rad_2, poi_q, pagetoken)
                for sumnya in dt_poi_q['results']:
                    if('rating' in sumnya):
                        if(float(sumnya['rating']) >= rating_tempat):
                            jum += 1
            jumlahnya = jum
                #jumlahnya+=len(dt_poi_q['results'])
            list_places_awal[loc_q].append(jumlahnya)
    return list_places_awal

# fungsi hitung entropy
def count_entropy(data):
    for n in range(0, len(data)):
        p = 0
        s = 0
        l = 0
        for m in range(3, len(data[n])):
            s = data[n][m]*0.01
            p += s + 1
            l = math.log(p)
        data[n].append(l)
    return data

# fungsi sort data
def sort_data(data):
    data.sort(key = lambda i: i[-1], reverse=True)
    for b in data:
        b.remove(b[-1])
    return data

# skyline function
def Skyline(datas, SelectingObject):
    output = []
    i = 0
    length = SelectingObject + 1
    while(i < len(datas)):
        c = 0
        j = 0
        while(j < len(datas)):
            worse = 0
            better = 0
            equal = 0
            for k in range(3, len(datas[0])):
                if(float(datas[i][k]) < float(datas[j][k])):
                    worse += 1
                elif(float(datas[i][k]) > float(datas[j][k])):
                    better += 1
                else:
                    equal += 1
            if(worse > 0 and equal + worse == length):
                c = 1
                datas.remove(datas[i])
                break
            elif(better > 0 and equal + better == length):
                datas.remove(datas[j])
            else:
                j += 1
        if(c != 1):
            i += 1
            output.append(i)
    return datas

