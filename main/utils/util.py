import random
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
