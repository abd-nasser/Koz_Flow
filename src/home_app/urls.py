from django.urls import path, include
from . import views

app_name = "home_app"

urlpatterns = [
    path("", views.home_page_view, name="home-page"),
    path("vehicules-vedette/partial/", views.vehicules_partial, name="vehicules-vedette-partial"),
    path("temoignages/", views.TemoignageListView.as_view(), name="temoignages-list"),
    path("avis-reseau/ajout/", views.CreateAvisReseauView.as_view(), name="ajout-avis-reseau"),
    path("avis-reseau/list/", views.ListeAvisReseauView.as_view(), name="avis-reseaux-list"),
    path("video-temoignages/", views.VideoTemoignageListView.as_view(), name="video-temoignages-list"),
    path("video-temoignages/ajout/", views.VideoTemoingnageCreateView.as_view(), name="ajout-video-temoignage"),
    path("temoignages/ajout/", views.TextuelTemoignageCreateView.as_view(), name="ajout-textuel-temoignage"),
    path("actualites/", views.ActualiteListView.as_view(), name="actualites-list"),
    path("actualites/ajouter/", views.ActualiteCreateView.as_view(), name="actualites-create"),
    path("actualites/<int:pk>/", views.ActualiteDetailView.as_view(), name="actualites-detail"),
    path("actualites/<int:pk>/modifier/", views.ActualiteUpdateView.as_view(), name="actualites-update"),
    path("actualites/<int:pk>/supprimer/", views.ActualiteDeleteView.as_view(), name="actualites-delete"),
]
