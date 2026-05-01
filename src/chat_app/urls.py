from django.urls import path
from . import views

app_name = "chat_app"

urlpatterns = [
   path('chat/<int:client_id>/', views.chat_view, name="chat-view"), #Commercial
   path('chat/', views.chat_view, name="chat-view"), #pour client
   path("chat/envoyer/<int:client_id>/", views.envoyer_message, name="envoyer-message")
]
