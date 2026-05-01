from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import (ApiRegisterView, LoginView, 
                    MeView, LogoutView,
                    UserRegisterView, ChangePasswordView)

app_name = "auth_app"

urlpatterns = [
    
    
    # Inscription
    path('register/', ApiRegisterView.as_view(), name='register'),
    # → http://127.0.0.1:8000/api/auth/register/
    
    #Connexion
    path('login/', LoginView.as_view(), name='login'),
    # → http://127.0.0.1:8000/api/auth/login/
    
    #Utilisateur connecté
    path('me/', MeView.as_view(), name="Me-view"),
    # → http://127.0.0.1:8000/api/auth/me/
    
    #Déconnexion
    path('logout/', LogoutView.as_view(), name="logout"),
    # → http://127.0.0.1:8000/api/auth/logout/
    
    # Rafraîchir le token (obtenir un nouveau access token avec le refresh token)
    path('token/refresh/', TokenRefreshView.as_view(), name='Token_refresh'),
    # → http://127.0.0.1:8000/api/auth/token/refresh/
    
    
    
    #-------------------------ERP  URLS-------------------
    #-------------------------ERP  URLS-------------------
    path("Userregister/",UserRegisterView.as_view(), name="user-register"),
    path("change_password/",ChangePasswordView.as_view(), name="change-password")
]
