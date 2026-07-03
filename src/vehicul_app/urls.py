from django.urls import path
from . import views

app_name = "vehicul_app"

urlpatterns = [
    path("nouveau/vehicule/", views.CreateVehiculView.as_view(), name="ajout-vehicul"),
    path("nouvelle/marque/", views.CreateMarqueView.as_view(), name="ajout-marque"),
    #Vehicul URLs
    path("list/vehicule/", views.VehiculListView.as_view(), name="list-vehicul"),
    path("detail/vehicule/<int:pk>/", views.VehiculDetailView.as_view(), name="detail-vehicul"),
    path("update/vehicule/<int:pk>/", views.VehiculUpdateView.as_view(), name="update-vehicul"),
    path("delete/vehicule/<int:pk>/", views.VehiculDeleteView.as_view(), name="delete-vehicul"),
    
    #Marque URLs
    path("list/marque/", views.MarqueListView.as_view(), name="list-marque"),
    path("detail/marque/<int:pk>/", views.MarqueDetailView.as_view(), name="detail-marque"),
    path("update/marque/<int:pk>/", views.MarqueUpdateView.as_view(), name="update-marque"),
    path("delete/marque/<int:pk>/", views.MarqueDeleteView.as_view(), name="delete-marque"),
    
     
    path('images/<int:pk>/', views.VehiculeImageListView.as_view(), name='vehicul-images-list'),
    path("suprrimer/image/<int:pk>/", views.VehiculeImageDeleteView.as_view(), name="delete-vehicul-image"),
    path("ajout/images/<int:pk>/", views.ajouter_image, name="ajouter-image"),
    
     # ✅ API publique
    path('api/vehicules/', views.APIVehiculListView.as_view(), name='api-vehicul-list'),
    path('api/vehicules/<int:pk>/',views.APIVehiculDetailView.as_view(), name='api-vehicul-detail'),
    ]