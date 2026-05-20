from django.urls import path
from .views import (
    CategorieProductsListView, CategorieProductsCreateView, CategorieProductsUpdateView, CategorieProductsDeleteView,
    ProductsListView, ProductsCreateView, ProductsDetailView, ProductsUpdateView, ProductsDeleteView,
    filter_products_by_category)
# products_app/urls.py

app_name = 'products_app'

urlpatterns = [
    # Catégories
    path('categories/', CategorieProductsListView.as_view(), name='categorie-products-list'),
    path('categories/ajouter/', CategorieProductsCreateView.as_view(), name='categorie-products-create'),
    path('categories/<int:pk>/modifier/', CategorieProductsUpdateView.as_view(), name='categorie-products-update'),
    path('categories/<int:pk>/supprimer/', CategorieProductsDeleteView.as_view(), name='categorie-products-delete'),
    
    # Produits
    path('', ProductsListView.as_view(), name='products-list'),
    path('ajouter/', ProductsCreateView.as_view(), name='products-create'),
    path('<int:pk>/', ProductsDetailView.as_view(), name='products-detail'),
    path('<int:pk>/modifier/', ProductsUpdateView.as_view(), name='products-update'),
    path('<int:pk>/supprimer/', ProductsDeleteView.as_view(), name='products-delete'),
    
    # Filtre
    path('categorie/<int:category_id>/', filter_products_by_category, name='products-by-category'),
]