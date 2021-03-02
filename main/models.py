from django.db import models


# Create your models here.

class Town(models.Model):
    name = models.CharField(max_length=255, primary_key=True)


class LevelType(models.Model):
    storey_range = models.CharField(max_length=255, primary_key=True)


class FlatType(models.Model):
    name = models.CharField(max_length=255)


class BlockAddress(models.Model):
    id = models.IntegerField(max_length=32, primary_key=True)
    block = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    town_name_id = models.ForeignKey(Town, on_delete=models.CASCADE)
    latitude = models.CharField(max_length=32, null=True, blank=True)
    longitude = models.CharField(max_length=32, null=True, blank=True)


class Room(models.Model):
    id = models.IntegerField(max_length=32, primary_key=True)
    flat_type_id = models.ForeignKey(FlatType, on_delete=models.CASCADE)
    level_type_id = models.ForeignKey(LevelType, on_delete=models.CASCADE)
    block_address_id = models.ForeignKey(BlockAddress, on_delete=models.CASCADE)
    resale_prices = models.IntegerField()
    remaining_lease = models.CharField(max_length=255)
    area = models.IntegerField()
