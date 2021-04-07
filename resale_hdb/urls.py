"""resale_hdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views

handler404 = views.handle404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test', views.test),

    path('map', views.map),
    path('', views.home_page_view),
    path('radar/', views.radar_view),
    path('town/<str:slug>', views.summary_view),
    path('price-prediction/', views.price_prediction_view),
]

api = [
    path('map/markers', views.map_markers_json),
    path('api/location-autocomplete', views.location_auto_complete_json),
    path('api/hdb-stats', views.StatsAPI.as_view()),
    path('api/price-prediction', views.PricePredictionAPI.as_view())
]

urlpatterns += api
