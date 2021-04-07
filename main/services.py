from math import floor

from main.models import Room, Town, FlatType


def calc_resale_price_rank(town):
    towns = Town.objects.all().order_by("-median_price")
    index = towns.index(town)
    return index + 1


def get_4_room_median_for_all_towns():
    towns = Town.objects.all()
    flat_type = FlatType.objects.get(name="4 ROOM")
    for town in towns:
        data_set = (
            Room.objects
            .filter(block_address__town_name=town, flat_type=flat_type)
            .order_by("resale_prices")
            .values_list("resale_prices", flat=True)
        )
        data_size = len(data_set)
        if data_size % 2 == 0:
            # Even
            mid = data_size/2 - 1
        else:
            mid = floor(data_size/2)

        median = data_set[int(mid)]
        town.median_price = median
        town.save()


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
