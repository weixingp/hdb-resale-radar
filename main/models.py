from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


# Create your models here.
from django.utils import timezone


class Town(models.Model):
    """
    HDB Neighbourhoods
    """
    name = models.CharField(max_length=255, unique=True)
    median_price = models.FloatField(null=True, blank=True)

    def get_slug(self):
        """
        :return: town in slug format
        """
        return self.name.lower().replace(" ", "-")


class LevelType(models.Model):
    """
    Level range type of flat
    """
    storey_range = models.CharField(max_length=255, unique=True)


class FlatType(models.Model):
    """
    Singapore HDB Flat types
    """
    name = models.CharField(max_length=255, unique=True)


class BlockAddress(models.Model):
    """
    A HDB block
    """
    block = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    town_name = models.ForeignKey(Town, on_delete=models.CASCADE)
    latitude = models.CharField(max_length=32, null=True, blank=True)
    longitude = models.CharField(max_length=32, null=True, blank=True)


class Room(models.Model):
    """
    A HDB room in a block
    """
    flat_type = models.ForeignKey(FlatType, on_delete=models.CASCADE)
    level_type = models.ForeignKey(LevelType, on_delete=models.CASCADE)
    block_address = models.ForeignKey(BlockAddress, on_delete=models.CASCADE)
    resale_prices = models.FloatField()
    remaining_lease = models.CharField(max_length=255)
    area = models.FloatField()
    resale_date = models.DateField(blank=True, null=True)


class NewsArticle(models.Model):
    """
    News articles crawled.
    """
    title = models.CharField(max_length=255)
    summary = models.TextField(max_length=1000)
    url = models.CharField(max_length=1028)
    source = models.CharField(max_length=255)
    img_url = models.CharField(max_length=1028)
    date = models.DateField(null=True, blank=True)

    def get_summary(self):
        return self.summary[:150] + "..."


class UserManager(BaseUserManager):
    """
    Extends Django User manager
    """
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    The User object
    """
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % self.pk


class Profile(models.Model):
    """
    The user profile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    has_updated_profile = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class FavouriteTown(models.Model):
    """
    User's favourite town
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    town = models.ForeignKey(Town, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'town')
