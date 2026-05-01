from django.urls import path
from . import views

app_name = "commercial_app"

urlpatterns = [
    path("dashboard/", views.CommercialDashboardView.as_view(), name="commercial-view")
]
