

from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import CategorieProducts, Products
from .forms import CategorieProductsForm, ProductsForm

# products_app/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from .models import CategorieProducts, Products
from .forms import CategorieProductsForm, ProductsForm

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
        return context

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