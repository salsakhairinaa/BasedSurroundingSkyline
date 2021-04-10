from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.forms import formset_factory
from .forms import SpatialForm, QueryForm
from .modul import  api, vs2
import pandas as pd
import numpy as np
import json
import csv

api_key = ""

# Create your views here.
def dashboard(request):
    context = {}
    QueryFormset = formset_factory(form=QueryForm, min_num=2, validate_min=True, extra=3)
    form = SpatialForm(request.POST or None)
    formset = QueryFormset(request.POST or None, prefix='query')
    if request.method == 'POST':
        if form.is_valid():
            print(form.cleaned_data['tipe_poi'], form.cleaned_data['min_rating'])
            if formset.is_valid():
                poi = form.cleaned_data['tipe_poi']
                tipe_poi = poi.replace('_', ' ').title()
                min_rating = form.cleaned_data['min_rating']
                data = []
                for que in formset:
                    cd = que.cleaned_data
                    tempat = cd.get('lokasi')
                    if tempat:
                        print(tempat)
                        data.append(tempat)
                query_data = pd.DataFrame(data)
                query_data.columns = ['nama']

                poi_data, query_data = api.get_poi(poi, query_data)
                poi_skyline = vs2.get_skyline_vs2(poi_data, query_data, min_rating)
            else:
                messages.info(request, "Lokasi yang dipertimbangkan minimal 2")
                return redirect('spatialskyline:dashboard')

            print(poi_data)
            print(query_data)
            print(poi_skyline)
            if len(poi_skyline) == 0:
                context['hasil'] = 'Tidak ada '+tipe_poi+' yang memenuhi minimum rating'
            intersection_cols = poi_skyline.index
            poi_not_skyline = poi_data.drop(intersection_cols)
            rows_skyline, rows_not_skyline, rows_query = poi_skyline.to_dict(orient='records'), poi_not_skyline.to_dict(orient='records'), query_data.to_dict(orient='records')
            data_skyline, data_not_skyline, data_query =  json.dumps(rows_skyline), json.dumps(rows_not_skyline), json.dumps(rows_query)
            data_skyline, data_not_skyline, data_query = json.loads(data_skyline), json.loads(data_not_skyline), json.loads(data_query)

            context['poi'] = tipe_poi
            context['skyline'] = data_skyline
            context['poi_data'] = data_not_skyline
            context['query_data'] = data_query
            context['api_key'] = api_key
            return render(request, 'spatialskyline/result.html', context)
        else:
            messages.info(request, "Jenis tempat tidak boleh kosong")
            return redirect('spatialskyline:dashboard')

    context['form'] = form
    context['formset'] = formset
    context['api_key'] = api_key
    return render(request, 'spatialskyline/dashboard.html', context)

def kueri(request):
    return render(request, 'spatialskyline/kueri.html')

def result(request):
    context = {}
    poi_awal = pd.read_csv('spatialskyline/modul/data_poi_daerah.csv')
    query_awal = pd.read_csv('spatialskyline/modul/data_query_daerah.csv')
    hasil = vs2.get_skyline_vs2(poi_awal, query_awal)
    hasil = hasil[:0]
    print(hasil)
    tipe_poi = 'Restaurant'
    if len(hasil) == 0:
        context['hasil'] = 'Tidak ada '+tipe_poi+' yang memenuhi minimum rating'
    intersection_cols = hasil.index
    poi = poi_awal.drop(intersection_cols)
    rows1, rows2, rows3 = hasil.to_dict(orient='records'), poi.to_dict(orient='records'), query_awal.to_dict(orient='records')
    data1, data2, data3 =  json.dumps(rows1), json.dumps(rows2), json.dumps(rows3)
    datas1, datas2, datas3 = json.loads(data1), json.loads(data2), json.loads(data3)
    print(len(hasil))
    print(len(poi))
    context['skyline'] = datas1
    context['poi_data'] = datas2
    context['query_data'] = datas3
    context['poi'] = 'Restaurant'
    context['api_key'] = api_key
    return render(request, 'spatialskyline/result.html', context)
