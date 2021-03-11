from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from main.APIManager import APIManager


def test(request):
    api = APIManager()
    api.load_data()
    api.import_to_database()

    return JsonResponse({"success": True})