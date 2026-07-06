# products_app/views.py
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import CategorieProducts, Products, ProductsImage
from .forms import CategorieProductsForm, ProductsForm, ProductImageForm

# ============================================================
# CRUD Catégories
# ============================================================

class CategorieProductsListView(ListView):
    model = CategorieProducts
    template_name = 'products_templates/categorie_products_list.html'
    context_object_name = 'categories'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'create_categorie_form' not in context:
            context['create_categorie_form'] = CategorieProductsForm()
        return context

class CategorieProductsCreateView(CreateView):
    model = CategorieProducts
    form_class = CategorieProductsForm
    template_name = 'products_templates/categorie_products_list.html'
    success_url = reverse_lazy('products_app:categorie-products-list')

class CategorieProductsUpdateView(UpdateView):
    model = CategorieProducts
    form_class = CategorieProductsForm
    template_name = 'products_templates/categorie_products_form.html'
    success_url = reverse_lazy('products_app:categorie-products-list')

class CategorieProductsDeleteView(DeleteView):
    model = CategorieProducts
    template_name = 'products_templates/categorie_products_confirm_delete.html'
    success_url = reverse_lazy('products_app:categorie-products-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Vous pouvez ajouter des messages de succès ici si vous utilisez le framework de messages de Django
        messages.success(self.request, "Nouvelle categorie ajoutée avec succès !")
        return response
    
    def form_invalid(self, form):
        listView = ProductsListView()
        listView.request = self.request  # Simule une requête pour pouvoir accéder aux catégories
        listView.object_list = listView.get_queryset() 
        listView.kwargs = self.kwargs
        context = listView.get_context_data()
        context['create_categorie_form'] = form # Formulaire avec les erreurs
        context["open_create_categorie_form"] = True # Indicateur pour ouvrir le modal
        
        messages.error(self.request, "Erreur lors de la création du catégories. Veuillez vérifier les informations saisies.")
        return self.render_to_response(context)


# ============================================================
# CRUD Produits
# ============================================================

class ProductsListView(ListView):
    model = Products
    template_name = 'products_templates/products_list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieProducts.objects.all()
        if 'create_product_form' not in context:
            context['create_product_form'] = ProductsForm()
        return context

class ProductsCreateView(CreateView):
    model = Products
    form_class = ProductsForm
    template_name = 'products_templates/products_list.html'
    success_url = reverse_lazy('products_app:products-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Vous pouvez ajouter des messages de succès ici si vous utilisez le framework de messages de Django
        messages.success(self.request, "Produit créé avec succès !")
        return response
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        listView = ProductsListView()
        listView.request = self.request  # Simule une requête pour pouvoir accéder aux catégories
        listView.object_list = listView.get_queryset() 
        listView.kwargs = self.kwargs
        context = listView.get_context_data()
        context['create_product_form'] = form # Formulaire avec les erreurs
        context["open_create_product_modal"] = True # Indicateur pour ouvrir le modal
        
        messages.error(self.request, "Erreur lors de la création du produit. Veuillez vérifier les informations saisies.")
        return self.render_to_response(context)

class ProductsDetailView(DetailView):  # ← DetailView, pas ListView !
    model = Products
    template_name = 'products_templates/products_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieProducts.objects.all()
        context['update_product_form'] = ProductsForm(instance=self.object)
        
         # ✅ Images du véhicule
        images = self.object.images.all().order_by('ordre', 'date_ajout')
        context["images"] = images
        
        # ✅ Image principale (fallback si pas trouvée)
        image_principal = images.filter(est_principale=True).first()
        if not image_principal and images.exists():
            image_principal = images.first()
        context["image_principal"] = image_principal
        return context

class ProductsImageListView(LoginRequiredMixin, ListView):
    model= ProductsImage
    template_name = 'products_templates/product_images_list.html'
    context_object_name = "images"
    paginate_by = 8
    
    def get_queryset(self):
        self.product = get_object_or_404(Products, pk=self.kwargs["pk"])
        return self.product.images.all().order_by('ordre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = self.product
        if "product_image_form" not in context:
            context["product_image_form"] = ProductImageForm()
        return context


# ============================================================================================
# ✅ AJOUT : Ajouter une Image(FBV)
# ============================================================================================
@login_required
@require_POST
def ajouter_image(request, pk):
    product = get_object_or_404(Products, pk=pk)
    
    #✅ Vérification des permissions
    if not (request.user.is_superuser or request.user.role =="directeur"):
        messages.error(request, "Vous n'avez pas la permission d'ajouter des images.")
        return redirect('products_app:products-detail', product.pk)
    
    #✅ Traitement de formulaire
    form = ProductImageForm(request.POST, request.FILES)
    if form.is_valid():
        image = form.save(commit=False)
        image.product = product
        image.save()
        
        #✅ SI l'image est Principale, désactiver les autres
        if image.est_principale:
            ProductsImage.objects.filter(
                product=product
            ).exclude(pk=image.pk).update(est_principale=False)
        messages.success(request, "✅ Image ajoutée avec succès")
    else:
        messages.error(request, f"❌ Erreur dans le formulaire:{form.errors}")
    
    #✅ Redirection vers la page d'images
    return redirect("products_app:product-images-list", product.pk)
        
        
        
#======================================================================================================
#✅ SUPPRESSION : Supprimer une Image 
#======================================================================================================
class ProductImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ProductsImage
    template_name = "products_templates/product_image_delete.html"
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    def get_success_url(self):
        return reverse_lazy('products_app:products-detail', kwargs={'pk': self.object.pk})
    def delete(self, request, *args, **kwargs):
        response =  super().delete(request, *args, **kwargs)
        messages.success(request, "Image supprimée avec succès")
        return response 


class ProductsUpdateView(UpdateView):
    model = Products
    form_class = ProductsForm
    template_name = 'products_templates/products_detail.html'

    def get_success_url(self):
        return reverse_lazy('products_app:products-detail', kwargs={'pk': self.object.pk})

class ProductsDeleteView(DeleteView):
    model = Products
    template_name = 'products_templates/confirm_products_delete.html'
    success_url = reverse_lazy('products_app:products-list')


# ============================================================
# Filtre par catégorie (FBV ou CBV au choix)
# ============================================================

# Option 1 : FBV (simple)
def filter_products_by_category(request, category_id):
    category = get_object_or_404(CategorieProducts, id=category_id)
    products = Products.objects.filter(categorie=category)
    return render(request, 'products_templates/products-list.html', {
        'products': products,
        'categories': CategorieProducts.objects.all()
    })

# Option 2 : CBV (plus propre)
class ProductsByCategoryListView(ListView):
    model = Products
    template_name = 'products_templates/products-list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return Products.objects.filter(categorie_id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorieProducts.objects.all()
        return context


# ============================================================
# API ProductLIST View
# ============================================================

from rest_framework import generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Products
from .serializers import ProductsSerializer

class ApiProductListView(generics.ListAPIView):
    queryset = Products.objects.all().select_related('categorie').prefetch_related("images")
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ["categorie__nom", "nom", "stock"]  # ← Ajout de stock
    
    search_fields = ['categorie__nom', "nom", "compatible_avec"]  # ← Suppression de stock (pas texte)
    
    ordering_fields = ['prix', 'stock', 'nom']  # ← Ajout de nom
    
    ordering = ['-id']  # ← Plus fiable que '-categorie__nom'
    

class ApiProductsdetail(generics.RetrieveAPIView):
    """
    API publique pour récuprer les details d'un produits
    """
    queryset = Products.objects.all().select_related("categorie").prefetch_related("images")
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    lookup_field = "pk"