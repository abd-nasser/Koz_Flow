# order_app/urls.py

from django.urls import path
from .views import (
    PanierDetailView,
    AjouterPanierView,
    ModifierArticlePanierView,
    RetirerArticlePAnierView,
    ViderPanierView
)

urlpatterns = [
    path('panier/', PanierDetailView.as_view(), name='panier-detail'),
    path('panier/ajouter/', AjouterPanierView.as_view(), name='panier-ajouter'),
    path('panier/modifier/<int:article_id>/', ModifierArticlePanierView.as_view(), name='panier-modifier'),
    path('panier/retirer/<int:article_id>/', RetirerArticlePAnierView.as_view(), name='panier-retirer'),
    path('panier/vider/', ViderPanierView.as_view(), name='panier-vider'),
]