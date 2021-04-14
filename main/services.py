import random
from math import floor

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.utils.timezone import localtime
from rest_framework.exceptions import ValidationError

from main.models import Room, Town, FlatType, FavouriteTown, Profile, NewsArticle
from main.utils.util import get_median
from resale_hdb.settings import DEFAULT_CACHE_TIME


def calc_resale_price_rank(town):
    cache_key = f"price_rank_{town.id}"
    cache_value = cache.get(cache_key)
    if cache_value is None:
        towns = Town.objects.all()
        index = list(towns.order_by("-median_price")).index(town)
        cache.set(cache_key, (towns, index), DEFAULT_CACHE_TIME)
    else:
        towns, index = cache_value

    return index + 1, len(towns)


def update_4_room_median_for_all_towns():
    towns = Town.objects.all()
    flat_type = FlatType.objects.get(name="4 ROOM")
    for town in towns:
        data_set = (
            Room.objects
            .filter(block_address__town_name=town, flat_type=flat_type)
            .order_by("resale_prices")
            .values_list("resale_prices", flat=True)
        )
        median = get_median(data_set)
        town.median_price = median
        town.save()


def get_4_room_median_for_town(town, year=None, month=None):
    cache_key = f"median_{town.id}_{year}_{month}"

    cache_value = cache.get(cache_key)
    if cache_value is not None:
        median = cache_value
    else:
        flat_type = FlatType.objects.get(name="4 ROOM")
        if year and month:
            data_set = (
                Room.objects
                .filter(
                    block_address__town_name=town,
                    flat_type=flat_type,
                    resale_date__year=year,
                    resale_date__month=month
                )
                .order_by("resale_prices")
                .values_list("resale_prices", flat=True)
            )
        else:
            data_set = (
                Room.objects
                .filter(
                    block_address__town_name=town,
                    flat_type=flat_type,
                )
                .order_by("resale_prices")
                .values_list("resale_prices", flat=True)
            )

        median = get_median(data_set)
        cache.set(cache_key, median, DEFAULT_CACHE_TIME)
    return median


def get_hdb_stats(town_id):
    town = Town.objects.get(id=town_id)
    rooms = Room.objects.filter(block_address__town_name=town)

    # --- Box plot ---
    """
    Box plot for min, max, q1, q3 and mean of different room type
    for a specific town.
    """
    room_types = rooms.order_by().values_list('flat_type__name', flat=True).distinct().order_by("flat_type__name")
    labels = []
    data_points = []
    for room_type in room_types:
        labels.append(room_type)
        points = list(rooms.filter(flat_type__name=room_type).values_list('resale_prices', flat=True))
        points_processed = []
        for point in points:
            points_processed.append(point/1000)

        data_points.append(points_processed)

    boxplot = {
        "labels": labels,
        "data": data_points
    }

    res = {
        "town_name": town.name,
        "boxplot": boxplot
    }

    return res


def get_all_towns():
    towns = Town.objects.all()
    return towns


def update_profile_town_favourite(user, town, remove=False):

    if not remove:
        FavouriteTown.objects.get_or_create(
            user=user,
            town=town,
        )
    else:
        obj = FavouriteTown.objects.filter(
            user=user,
            town=town
        )
        if obj:
            obj[0].delete()


def create_user_profile(user):
    profile, created = Profile.objects.get_or_create(
        user=user,
    )

    return profile


def get_fav_towns(user):
    fav_towns = FavouriteTown.objects.filter(
        user=user
    )

    towns = []
    for item in fav_towns:
        towns.append(item.town)

    return towns


def update_fav_town(user, town_id, is_unfav):

    try:
        town = Town.objects.get(id=town_id)
    except ObjectDoesNotExist:
        raise ValidationError(detail="town does not exist")

    if is_unfav:
        fav_town = FavouriteTown.objects.filter(
            user=user,
            town=town
        )
        if fav_town:
            fav_town = fav_town[0]
            fav_town.delete()
    else:
        FavouriteTown.objects.get_or_create(
            town=town,
            user=user
        )


def check_is_fav(user, town):
    fav_town = FavouriteTown.objects.filter(
        user=user,
        town=town
    )

    if not fav_town:
        return False
    else:
        return True


def get_news_for_display(n=10):
    sources = [
        "Straits Times",
        "MotherShip"
    ]

    news_list = []
    for source in sources:
        limit = floor(n/len(sources))
        temp_list = list(NewsArticle.objects.filter(source=source).order_by("-date")[:limit])
        news_list += temp_list

    news_list.sort(key=lambda x: x.date, reverse=True)

    return news_list


def get_random_latest_flats(n=10):
    res = []
    for i in range(0, n):
        max_id = Room.objects.all().aggregate(max_id=Max("id"))['max_id']
        min_id = max_id - 5000
        while True:
            pk = random.randint(min_id, max_id)
            flat = Room.objects.filter(pk=pk).first()
            if flat and flat not in res:
                res.append(flat)
                break

    return res
