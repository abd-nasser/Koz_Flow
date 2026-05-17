from django.urls import path
from . import views

app_name = "commercial_app"

urlpatterns = [
    path("dashboard/", views.CommercialDashboardView.as_view(), name="commercial-view"),
    path("générer/<int:demande_id>/offre/", views.creer_offre, name="creer-offre"),
    path("offres/", views.OffreView.as_view(), name="offre-list"),
    path("offre/<int:pk>/", views.OffreDetailView.as_view(), name="offre-detail"),  
    path("offre/<int:offre_id>/accepter/", views.accepter_offre, name="accepter-offre"),
    path("offre/<int:offre_id>/refuser/", views.refuser_offre, name="refuser-offre"),
]
