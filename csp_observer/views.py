from django.shortcuts import render
from django.http import HttpResponse

def report(request):
    return HttpResponse("Hello, World!")