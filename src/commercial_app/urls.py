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
    
    #######################________Maintenance____________#############################
    path('maintenances/',views.MaintenanceListView.as_view(), name='maintenance-list'),
    path('maintenances/ajouter/',views.MaintenanceCreateView.as_view(), name='maintenance-create'),
    path('maintenances/<int:pk>/',views.MaintenanceDetailView.as_view(), name='maintenance-detail'),
    path('maintenances/<int:pk>/modifier/',views.MaintenanceUpdateView.as_view(), name='maintenance-update'),
    path('maintenances/<int:pk>/supprimer/',views.MaintenanceDeleteView.as_view(), name='maintenance-delete'),
]
