import random
import re
from math import floor

from django.db.models import Max

from main.models import NewsArticle, Room


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


def get_storey_range(item, reverse=False):

    level_options = {
        '01 TO 03': 'Very Low',
        '04 TO 06': 'Low',
        '07 TO 09': 'Intermediate',
        '10 TO 12': 'High',
        'OTHERS': 'Very High',
        'UNDEFINED': 'Unknown'
    }

    if not reverse:
        level_name = item
        try:
            level = level_options[level_name]
        except KeyError:
            level = re.search(r'\d+', level_name).group()
            if level:
                level = int(level)
                if level >= 13:
                    level = level_options['OTHERS']
                else:
                    level = level_options['UNDEFINED']
            else:
                level = level_options['UNDEFINED']
    else:
        level = None
        for key, value in level_options.items():
            if value == item:
                level = key
                break

    return level


def get_median(data_set):
    data_size = len(data_set)
    if data_size % 2 == 0:
        # Even
        mid = data_size / 2 - 1
    else:
        mid = floor(data_size / 2)

    median = data_set[int(mid)]

    return median
