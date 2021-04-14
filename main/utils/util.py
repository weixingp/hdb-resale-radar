import random
import re
from math import floor

from django.db.models import Max

from main.models import NewsArticle, Room


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
