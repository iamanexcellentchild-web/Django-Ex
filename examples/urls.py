from django.urls import path

from examples.views import home, search

urlpatterns = [
    path("", home, name="home"),
    path("search/", search, name="search"),
]
