from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader
from rest_framework.response import Response
from rest_framework.views import APIView

from main.APIManager import APIManager
from main.models import Town, BlockAddress, NewsArticle, Room, FlatType
from main.services import get_hdb_stats
from main.utils.util import get_news_for_display, get_random_latest_flats


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
    template = loader.get_template('new/index.html')

    # Crawled News
    news_list = get_news_for_display(n=6)

    # Stats - To be implemented as API instead
    total_data = Room.objects.all().count()
    total_towns = Town.objects.all().count()

    latest_sold_flats = get_random_latest_flats(n=10)

    context = {
        "news_list": news_list,
        "total_data": total_data,
        "total_towns": total_towns,
        "latest_sold_flats": latest_sold_flats
    }
    response = HttpResponse(template.render(context, request))
    return response


def radar_view(request):
    template = loader.get_template('new/radar.html')
    towns = Town.objects.all()
    context = {
        "towns": towns,
    }

    response = HttpResponse(template.render(context, request))
    return response


def location_auto_complete_json(request):
    # To be migrated to api view
    towns = Town.objects.all()
    res = []
    for town in towns:
        temp = {
            "label": town.name,
            "value": town.name,
        }
        res.append(temp)

    return JsonResponse(res, safe=False)


def summary_view(request):
    template = loader.get_template('new/summary.html')
    context = {
        "town": Town.objects.get(id=5)
    }

    response = HttpResponse(template.render(context, request))
    return response


class StatsAPI(APIView):

    def get(self, request):
        town_id = request.GET.get("tid")
        stats = get_hdb_stats(town_id)

        return Response(stats)

