from django.urls import path
from . import views
app_name = "leads_app"

urlpatterns = [
    path('demande/de/financement/<int:vehicul_id>/',views.demande_financement_view, name="demande-financement"),
    path("attente/de/document/<int:demande_id>/",views.attente_document, name="attente-document" ),
    path("upload/document/<int:demande_id>",views.upload_multiple_documents, name="upload-document"),
    path('demande/<int:demande_id>/accorder/', views.accorder_demande, name='accorder-demande'),
    path('demande/<int:demande_id>/refuser/', views.refuser_demande, name='refuser-demande'),
    
    path("liste/demande/de/financement/", views.DemandeFinView.as_view(), name="list-demande-financement"),
    path("details/demande/financement/<int:pk>/",views.DemandeDetailView.as_view(), name="detail-demande"),
    path("gestion/type/financement/<int:pk>/", views.GestionTypeFinancementView.as_view(), name="gestion-type-financement"),
    
    
   
]
