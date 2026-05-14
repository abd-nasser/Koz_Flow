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
    
    ##############################_____DOCUMENT_URLS_______############################################
    
    path("liste/documents/", views.DocumentListView.as_view(), name="documents-list"),
    path("document/<int:pk>/detail/", views.DocumentDetailView.as_view(), name="document-detail"),
    path("modifier/<int:pk>/document/", views.DocumentUpdateView.as_view(), name="document-update"),
    path("document/<int:pk>/supprimer/", views.DocumentDeleteView.as_view(), name="document-delete"),
    
    ###############################GESTION STATUTS DOCUMENTS##############################
    path("document/<int:dossier_id>/valider/", views.valide_dossier, name="valider-document"),
    path("document/<int:dossier_id>/rejeter/", views.rejete_dossier, name="rejeter-document"),
    path("document/<int:dossier_id>/verifier/", views.verifier_dossier, name="verifier-document"),
    path("document/<int:dossier_id>/modifier/", views.modifier_dossier, name="modifier-document"),
   
]