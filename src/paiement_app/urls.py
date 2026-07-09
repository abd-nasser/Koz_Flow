from django.urls import path
from . import views

urlpatterns = [
    path("paiement/initier/", views.ApiPaiementView.as_view(), name="api-paiement-initier"),
    path("paiement/callback/", views.callback_ligdicash, name="callback-ligdicash"),
]
