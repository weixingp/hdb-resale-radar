from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader

from main.APIManager import APIManager
from main.models import Town, BlockAddress, NewsArticle


def test(request):
    api = APIManager()
    api.load_data()
    api.import_to_database()

    return JsonResponse({"success": True})


def map_markers_json(request):
    towns = Town.objects.all()

    res = []
    for town in towns:
        location = BlockAddress.objects.filter(town_name=town)[0]
        coord = [location.latitude, location.longitude]
        temp = {
            "name": town.name,
            "location": coord,
        }
        res.append(temp)

    return JsonResponse(res, safe=False)


def map(request):
    template = loader.get_template('map/google_map_with_markers.html')
    context = {
    }
    response = HttpResponse(template.render(context, request))
    return response


def home_page_view(request):
    template = loader.get_template('main/index.html')

    # Crawled News
    news_list = NewsArticle.objects.filter().order_by("-id")[:10]

    context = {
        "news_list": news_list
    }
    response = HttpResponse(template.render(context, request))
    return response
