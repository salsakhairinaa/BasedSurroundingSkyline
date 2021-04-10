from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core import serializers
import math
import requests
import json
from . forms import FilterForm
from .modul import api
import pandas as pd
import numpy as np
from django.http import JsonResponse
from django.template.loader import render_to_string

api_key = ""

# menerima input data dari user untuk filter pertama
def dashboard(request):
	context = {}
	form = FilterForm(request.POST or None)
	if request.method =='POST':
		
		if form.is_valid():
			location_target = form.cleaned_data['location_target']
			target_type     = form.cleaned_data['target_type']
			radius_target   = form.cleaned_data['radius_target']
			object_type     = form.cleaned_data['object_type']
			radius_object   = form.cleaned_data['radius_object']
			rating          = form.cleaned_data['rating']
			selecting_object=len(object_type)

			if radius_object>50000:
				return render(request, 'basedsurrounding/dashboard.html', {'form':form, 'errors': 'Silakan masukan radius kurang dari 50.000 meter'})	

			if radius_target>50000:
				return render(request, 'basedsurrounding/dashboard.html', {'form':form, 'errors': 'Silakan masukan radius kurang dari 50.000 meter'})	

			# Untuk tipe lokasi untuk di halaman result
			fix_lokasi = target_type.replace("_", " ")
			#print(fix_lokasi)
			tipe_lokasi = fix_lokasi.title()
			#print(tipe_lokasi)

			# Untuk nama header di halaman result
			fix=[j.replace("_", " ") for j in object_type]
			#print(fix)
			tipe_objek = [ i.title() for i in fix]
			#print(tipe_objek)


			#get geo for result.html
			for_result = api.get_geometry_target(location_target)
			geo_target = for_result[0]+','+for_result[1]
			lat = for_result[0]
			lng = for_result[1]
			# print(for_result)
			# print(geo_target)
			
			#get surrounding object
			surrounding_object = api.get_object(geo_target, str(radius_target), target_type)
			s_o = pd.DataFrame(surrounding_object)
			print(s_o)
			
			#get geo object
			geo = api.get_geo(surrounding_object)
			g = pd.DataFrame(geo)
			print(g)
			
			#get sum objects
			result = api.get_sum_facilities(object_type, geo, rating, str(radius_object), surrounding_object )
			r = pd.DataFrame(result)
			print(r)
			
			# get entropy
			entropy_data = api.count_entropy(result)
			e_d = pd.DataFrame(entropy_data)
			print(e_d)
			
			#sort data
			data_sort = api.sort_data(entropy_data)
			d_s = pd.DataFrame(data_sort)
			print(d_s)
			
			# get skyline
			skyline_result = api.Skyline(data_sort, selecting_object)
			s_r = pd.DataFrame(skyline_result)
			print(s_r)
			

			# # json file

			#json api key
			# key_api = json.dumps(api_key)
			# api_key = json.loads(key_api)
			# api_d = render_to_string('basedsurrounding/result.html', {"classes": api_key})

			# json geometry location_target
			dt = json.dumps(for_result)
			dts = json.loads(dt)
			dts_d = render_to_string('basedsurrounding/result.html', {"classes": dts})

			#json object_type for header table
			objects = json.dumps(tipe_objek)
			object_count = json.loads(objects)
			object_count_header = render_to_string('basedsurrounding/result.html', {"classes": object_count})

			#json untuk nama jenis lokasi
			lok = json.dumps(tipe_lokasi)
			tipe_lok = json.loads(lok)
			tipe_lok_name = render_to_string('basedsurrounding/result.html', {"classes": tipe_lok})

			#tes tanpa menggunakan goole maps api
			#poi_awal = pd.read_csv('basedsurrounding/modul/query.csv')

			#json data skyline
			rows = s_r.to_dict(orient='records')
			data =  json.dumps(rows)
			datas = json.loads(data)
			# remove lat and long from input
			for i in datas:
				i.pop("1")
				i.pop("2")
			datas_d = render_to_string('basedsurrounding/result.html', {"classes": datas})

			#json lat n long for maps
			row = s_r.to_dict(orient='records')
			data_geo =  json.dumps(row)
			datas_geo = json.loads(data)
			datas_geo_latlong = render_to_string('basedsurrounding/result.html', {"classes": datas_geo})

			return render(request, 'basedsurrounding/result.html', { 'datas': datas, "object_count": object_count, "dts": dts, "datas_geo": datas_geo, "tipe_lok":tipe_lok
				})
			#return render(request, 'basedsurrounding/dashboard.html', {'form':form})
		else:
			messages.info(request, "Silakan lengkapi data")
			return redirect('basedsurrounding:dashboard')
	else:
		# form = FilterForm()
		context['form'] = form
		return render(request, 'basedsurrounding/dashboard.html', context)
