# Modul Pengumpulan Data

### Import Library
# 1. __requests__ untuk get data menggunakan url
# 2. __json__ untuk mengolah data hasil request yang berbentuk json
# 3. __pandas__ untuk mengolah dataframe
# 4. __time__ untuk delay saat request data
import requests
import json
import pandas as pd
import time

### API KEY
# API Key Google Maps diperoleh setelah Registrasi sebagai developer dan menggunakan plan FREE.
# Plan FREE dapat digunakan hingga satu tahun dengan kredit yang diberikan sebesar $300.
# https://cloud.google.com/maps-platform/
api_key = ''

### API yang digunakan
# API yang digunakan ada tiga jenis yaitu:
# 1. __Place API - Nearby Search__ (url_nearbysearch), digunakan untuk request data POI
# (https://developers.google.com/places/web-service/search#PlaceSearchRequests)
# 2. __Geocoding API__ (url_geocode), digunakan untuk request data query
# (https://developers.google.com/maps/documentation/geocoding/start)
url_nearbysearch = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
url_geocode = 'https://maps.googleapis.com/maps/api/geocode/json?'

#### Fungsi get_request_poi
# *get_request_poi* melakukan request data menggunakan __url_textsearch__ untuk memperoleh data mengenai poi yang
# diinginkan dengan parameter yang digunakan yaitu jenis_poi (cafe, restoran, hotel, dll) dan daerah pencariannya
# (Bogor, Jakarta, Bandung, dll). Request data akan menghasilkan maksimal 60 data POI teratas berdasarkan
# rank/keunggulan dari POI dengan format *json*. Total 60 data POI terbagi dalam 3 page berbeda yang ditampilkan
# satu persatu. Untuk mengakses page kedua dan ketiga digunakan *pagetoken* dari hasil request.
# Oleh karena itu, terdapat dua kondisi dalam fungsi ini yaitu dengan *pagetoken* dan tanpa *pagetoken*
# (hasil request data page pertama).
def get_request_poi(jenis_poi, lokasi, pagetoken=None):
    if pagetoken:
        request_poi = requests.get(url_nearbysearch+'pagetoken='+pagetoken+'&key='+api_key)
    else:
        request_poi = requests.get(url_nearbysearch+'location='+lokasi+'&radius=5000'+'&type='+jenis_poi+'&key='+api_key)
    hasil = json.loads(request_poi.text)

    return hasil

#### Fungsi get_poi_data
# *get_poi_data* melakukan pengolahan data yang dihasilkan dari fungsi *get_request_data*.
# Pengolahan yang dilakukan berupa pengambilan informasi yang dibutuhkan saja
# (nama, rating, latitude, longitude, dan place id dari POI) yang kemudian disimpan dalam bentuk *list*.
def get_poi_data(list_poi, list_data_poi):
    for poi in list_poi['results']:
        baris = []
        nama = poi['name']
        if 'rating' in poi:
            rating = poi['rating']
        else:
            rating = 0
        latitude, longitude = poi['geometry']['location']['lat'], poi['geometry']['location']['lng']
        baris.append(nama)
        baris.append(rating)
        baris.append(latitude)
        baris.append(longitude)
        list_data_poi.append(baris)

#### Fungsi get_query_data
# *get_query_data* melakukan request data menggunakan __url_geocode__ untuk memperoleh informasi mengenai query yang ada.
# Pada fungsi ini juga langsung dilakukan pengolahan data untuk mengambil informasi yang diperlukan dari hasil request
# (nama, latitude, longitude, dan place id).
def get_query_data(query_data):
    location_query = []
    for query in query_data['nama']:
        baris = []
        request_query = requests.get(url_geocode+'address='+query+'&key='+api_key)
        print("Sedang melakukan request data query "+query)
        location = json.loads(request_query.text)
        latitude = location['results'][0]['geometry']['location']['lat']
        longitude = location['results'][0]['geometry']['location']['lng']
        baris.append(latitude)
        baris.append(longitude)
        location_query.append(baris)
    location_lat = [loc[0] for loc in location_query]
    query_data.insert(loc = len(query_data.columns), column = 'latitude', value = location_lat)
    location_lng = [loc[1] for loc in location_query]
    query_data.insert(loc = len(query_data.columns), column = 'longitude', value = location_lng)
    print("Data berhasil diperoleh dengan total "+str(len(query_data))+" query")

    return query_data

#### Fungsi get_poi
# *get_poi* merupakan fungsi utama yang menjalankan fungsi lainnya.
# Parameter yang dibutuhkan yaitu jenis POI dan query
# Hasil dari fungsi ini berupa dataframe informasi POI dan query
def get_poi(poi, query):
    list_data_poi = []
    i = 1
    total = 3

    data_query = get_query_data(query)
    lat, lng = data_query['latitude'].mean(), data_query['longitude'].mean()
    lokasi = str(lat)+','+str(lng)

    hasil = get_request_poi(poi, lokasi)
    print("Sedang melakukan request data "+str(i)+" dari "+str(total)+"...")
    get_poi_data(hasil, list_data_poi)
    while 'next_page_token' in hasil:
        i += 1
        pagetoken = hasil['next_page_token']
        time.sleep(5)
        print("Sedang melakukan request data "+str(i)+" dari "+str(total)+"...")
        hasil = get_request_poi(poi, lokasi, pagetoken)
        get_poi_data(hasil, list_data_poi)
    print("Data berhasil diperoleh. Total "+str(len(list_data_poi))+" data.")

    list_data_poi = pd.DataFrame(list_data_poi)
    list_data_poi.columns = ['nama_poi', 'rating', 'latitude', 'longitude']

    data_poi = list_data_poi.drop_duplicates(subset=['latitude', 'longitude'], keep='first')
    print("Total data tanpa duplikat titik lokasi sebanyak "+str(len(data_poi))+" data.")

    return data_poi, data_query
