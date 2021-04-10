from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

def welcome(request):
    return render(request, 'welcome.html')
