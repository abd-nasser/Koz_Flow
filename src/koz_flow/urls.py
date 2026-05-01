
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("home_app.urls")),
    path('api/auth/', include('auth_app.urls')),
    path("directeur/", include("directeur_app.urls")),
    path("commercial/", include("commercial_app.urls")),
    path('client/', include("client_app.urls")),
    path('chat/', include("chat_app.urls")),
    
    path('admin/', admin.site.urls),
]
