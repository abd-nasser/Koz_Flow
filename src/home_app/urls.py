from django.urls import path, include
from . import views

app_name = "home_app"

urlpatterns = [
    path("", views.home_page_view, name="home-page"), 
    path("vehicules-vedette/partial/", views.vehicules_partial, name="vehicules-vedette-partial") 
]
