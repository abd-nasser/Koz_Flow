from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("home_app.urls")),
    path('api/auth/', include('auth_app.urls')),
    path("directeur/", include("directeur_app.urls")),
    path("commercial/", include("commercial_app.urls")),
    path('client/', include("client_app.urls")),
    path('chat/', include("chat_app.urls")),
    path('vehicule/', include("vehicul_app.urls")),
    
    path('admin/', admin.site.urls),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)