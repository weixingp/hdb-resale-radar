from main.models import Room, Town


def get_hdb_stats(town_id):
    town = Town.objects.get(id=town_id)
    rooms = Room.objects.filter(block_address__town_name=town)

    # --- Box plot ---
    """
    Box plot for min, max, q1, q3 and mean of different room type
    for a specific town.
    """
    room_types = rooms.order_by().values_list('flat_type__name', flat=True).distinct()
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
