from django.db import models


# Create your models here.

class Town(models.Model):
    name = models.CharField(max_length=255, unique=True)
    median_price = models.FloatField(null=True, blank=True)

    def get_slug(self):
        return self.name.lower().replace(" ", "-")


class LevelType(models.Model):
    storey_range = models.CharField(max_length=255, unique=True)


class FlatType(models.Model):
    name = models.CharField(max_length=255, unique=True)


class BlockAddress(models.Model):
    block = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    town_name = models.ForeignKey(Town, on_delete=models.CASCADE)
    latitude = models.CharField(max_length=32, null=True, blank=True)
    longitude = models.CharField(max_length=32, null=True, blank=True)


class Room(models.Model):
    flat_type = models.ForeignKey(FlatType, on_delete=models.CASCADE)
    level_type = models.ForeignKey(LevelType, on_delete=models.CASCADE)
    block_address = models.ForeignKey(BlockAddress, on_delete=models.CASCADE)
    resale_prices = models.FloatField()
    remaining_lease = models.CharField(max_length=255)
    area = models.FloatField()
    resale_date = models.DateField(blank=True, null=True)


class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(max_length=1000)
    url = models.CharField(max_length=1028)
    source = models.CharField(max_length=255)
    img_url = models.CharField(max_length=1028)
    date = models.DateField(null=True, blank=True)

    def get_summary(self):
        return self.summary[:150] + "..."
