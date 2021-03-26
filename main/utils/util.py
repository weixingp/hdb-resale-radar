from math import floor

from main.models import NewsArticle


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
