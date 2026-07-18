from django.urls import path, include
from . import views

app_name = "home_app"

urlpatterns = [
    path("", views.home_page_view, name="home-page"),  
]
