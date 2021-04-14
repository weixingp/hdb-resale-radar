from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse

# Create your views here.
from django.shortcuts import redirect
from django.template import loader
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from main.APIManager import APIManager
from main.forms import PricePredictionForm, FavTownForm
from main.models import Town, BlockAddress, NewsArticle, Room, FlatType, LevelType
from main.services import get_hdb_stats, get_all_towns, update_profile_town_favourite, create_user_profile, \
    get_fav_towns, calc_resale_price_rank, get_4_room_median_for_town, update_fav_town, check_is_fav, \
    get_news_for_display, get_random_latest_flats, get_total_towns, get_n_mths_median
from main.utils.PricePredictionModel import PricePredictionModel
from main.utils.util import get_storey_range


def profile_setup_required(function):
    def _function(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect("/account/setup/")

        return function(request, *args, **kwargs)

    return _function


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

    towns = get_all_towns()
    for town in towns:
        rank, total = calc_resale_price_rank(town)
        four_room_median = get_4_room_median_for_town(town)
        town.rank = rank
        town.median = int(four_room_median)

    context = {
        "towns": towns,
        "total_towns": len(towns),
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


def summary_view(request, slug):
    template = loader.get_template('new/summary.html')
    town_name = slug.replace("-", " ").upper()
    try:
        town = Town.objects.get(name=town_name)
        all_town = get_all_towns()
        rank, total_towns = calc_resale_price_rank(town)
        is_fav = False
        if request.user.is_authenticated:
            is_fav = check_is_fav(user=request.user, town=town)

    except ObjectDoesNotExist:
        return redirect("/404")

    context = {
        "town": town,
        "rank": rank,
        "total_towns": total_towns,
        "is_fav": is_fav,
        "all_towns": all_town
    }

    response = HttpResponse(template.render(context, request))
    return response


@login_required
def price_prediction_view(request):
    template = loader.get_template('new/price_prediction.html')
    flat_types = FlatType.objects.all()
    level_types = LevelType.objects.all().order_by("-storey_range")
    towns = Town.objects.all().order_by("name")
    for level in level_types:
        level_range = get_storey_range(level.storey_range, reverse=True)
        level.storey_range = f"{level.storey_range} ({level_range})"

    context = {
        "flat_types": flat_types,
        "level_types": level_types,
        "towns": towns,
    }

    response = HttpResponse(template.render(context, request))
    return response


class StatsAPI(APIView):

    def get(self, request):
        town_id = request.GET.get("tid")
        # try:
        stats = get_hdb_stats(town_id)
        # except Exception:
        #     raise ValidationError(detail="Something went wrong.")

        return Response(stats)


class PricePredictionAPI(APIView):

    def post(self, request):
        form = PricePredictionForm(request.POST)
        if form.is_valid():
            user_input = [[
                form.cleaned_data['area'],
                form.cleaned_data['town'],
                form.cleaned_data['flat_type'],
                form.cleaned_data['level_type'],
                f"{form.cleaned_data['remaining_lease']} Years"
            ]]
            print(user_input)
            ppm = PricePredictionModel()
            try:
                result = ppm.prediction_for_user_input(user_input)
                res = {
                    "success": True,
                    "result": result,
                }
            except Exception as ex:
                print(repr(ex))
                error = "Result not available with your conditions, try changing to some of your conditions."
                res = {
                    "success": False,
                    "err": error,
                }
        else:
            error = "Please check that all required fields are filled."
            res = {
                "success": False,
                "err": error
            }

        return Response(res)


def handle404(request, exception):
    template = loader.get_template("new/404.html")
    context = {}
    response = HttpResponse(template.render(context, request))
    return response


@login_required
def account_setup_view(request):
    template = loader.get_template("account/setup.html")
    towns = get_all_towns()
    user = request.user

    # Redirects the user to dashboard if he has setup his profile
    if hasattr(user, "profile"):
        return redirect("/dashboard")

    if request.method == "POST":
        profile = create_user_profile(user)
        profile.has_updated_profile = True
        profile.save()
        for town in towns:
            select = request.POST.get(f'town-{town.id}')
            if select is not None:
                if select == '1':
                    update_profile_town_favourite(user, town)
        return redirect("/dashboard")
    else:
        context = {
            "towns": towns,
        }
        response = HttpResponse(template.render(context, request))
        return response


@login_required
@profile_setup_required
def dashboard_view(request):
    template = loader.get_template("new/dashboard.html")
    user = request.user
    fav_towns = get_fav_towns(user)

    towns = []
    for town in fav_towns:
        rank, total = calc_resale_price_rank(town)
        four_room_median = get_4_room_median_for_town(town)
        town.rank = rank
        town.median = int(four_room_median)
        towns.append(town)

    context = {
        "favourite_towns": towns,
        "total_towns": get_total_towns(),
    }

    response = HttpResponse(template.render(context, request))
    return response


class TownFavAPI(APIView):

    @method_decorator(login_required)
    def post(self, request):
        form = FavTownForm(request.data)
        user = request.user
        if form.is_valid():
            town_id = form.cleaned_data['town_id']
            is_unfav = form.cleaned_data['is_unfav']
            update_fav_town(user=user, town_id=town_id, is_unfav=is_unfav)
        else:
            print(form.errors)
            raise ValidationError(detail="Invalid data")

        return Response({"success": True})
