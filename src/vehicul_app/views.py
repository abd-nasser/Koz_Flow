from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView,DetailView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import HttpResponse



from django.db.models import Q
from django.urls import reverse_lazy 

from .models import Vehicul, Marque, VehiculeImage
from .forms import VehiculForm, MarqueForm, VehiculeImage, VehiculeImageFormSet, VehiculeImageForm
from directeur_app.views import DirecteurDashboardView
from leads_app.forms import DemandeFinancementForm


class CreateMarqueView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Marque
    form_class = MarqueForm
    template_name = "directeur_templates/directeur.html"
    success_url = reverse_lazy("directeur_app:directeur-view")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Nouvelle marque ajoutée")
        return response
            
        
    
    def form_invalid(self, form):
        dashboard = DirecteurDashboardView()
        dashboard.request = self.request
        context = dashboard.get_context_data()
        context["marque_form"] = form
        context["open_marque_modal"] = True
        return self.render_to_response(context)
    
class MarqueListView(LoginRequiredMixin, ListView):
    model = Marque
    template_name = "vehicul_templates/marque_list.html"
    context_object_name = "marque_list"

class MarqueDetailView(LoginRequiredMixin, DetailView):
    model = Marque
    template_name = "vehicul_templates/marque_detail.html"
    context_object_name = "marque"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "marque_form" not in context:
            context["marque_form"] = MarqueForm(instance=self.object)
        return context
    

class MarqueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Marque
    form_class = MarqueForm
    template_name = "vehicul_templates/marque_detail.html"
    
    def get_success_url(self):
        return reverse_lazy("vehicul_app:detail-marque", kwargs={"pk": self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Marque mise à jour avec succès")
        return response
    
    def form_invalid(self, form):
        dashboard = MarqueListView()
        dashboard.request = self.request
        dashboard.kwargs = self.kwargs
        dashboard.object = self.get_object()
        dashboard.object_list = self.get_queryset()
        context = dashboard.get_context_data()
        
        context["marque_form"] = form
        context["open_marque_modal"] = True
        return self.render_to_response(context)
    
    
class MarqueDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
        
    model = Marque
    template_name = "vehicul_templates/detail_marque.html"
    success_url = reverse_lazy("vehicul_app:list-marque")
        

#========================================= Vehicul Views =========================================




from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Vehicul, VehiculeImage

    

class CreateVehiculView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Vehicul
    form_class = VehiculForm
    template_name = "directeur_templates/directeur.html"
    success_url = reverse_lazy("directeur_app:directeur-view")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Nouvelle voiture ajoutée")
        return response
        
    def form_invalid(self, form):
        dashboard = DirecteurDashboardView()
        dashboard.request = self.request
        context = dashboard.get_context_data()
        
        context["vehicul_form"] = form
        context["open_vehicul_modal"] = True
        return self.render_to_response(context)
        
    
class VehiculListView(LoginRequiredMixin, ListView):
    model = Vehicul
    context_object_name ="vehicul_list"
    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["partials/vehiculs/partials_vehicul_list.html"]
        
        return ["vehicul_templates/vehicul_list.html"]
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marques"] = Marque.objects.all()
        context["TYPES_CARBURANT"] = Vehicul.TYPES_CARBURANT_CHOICES
        
        # ✅ Ajout de l'image principale pour chaque véhicule
        for vehicule in context["vehicul_list"]:
            image_principale = vehicule.images.filter(est_principale=True).first()
            vehicule.image_display = image_principale.image if image_principale else vehicule.image_principale
        
        return context
    
    def get_queryset(self):
        queryset = Vehicul.objects.all().select_related("marque").order_by("-date_ajout")
        
        search_query = self.request.GET.get("q")
        marque = self.request.GET.get("marque")
        carburant = self.request.GET.get("carburant")
        
        if search_query:
            queryset = queryset.filter(
                Q(modele__icontains=search_query) |
                Q(marque__nom__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(annee__icontains=search_query) |
                Q(carburant__icontains=search_query) |
                Q(kilometrage__icontains=search_query) |
                Q(prix__icontains=search_query)
            )
        
        if marque:
            queryset = queryset.filter(marque__nom=marque)
        
        if carburant:
            queryset = queryset.filter(carburant=carburant)
        
        return queryset
               
class VehiculDetailView(LoginRequiredMixin, DetailView):
    model = Vehicul
    template_name = "vehicul_templates/vehicul_detail.html"
    context_object_name = "vehicul"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulaire de modification
        if "vehicul_form" not in context:
            context["vehicul_form"] = VehiculForm(instance=self.object)
        
        # Formulaire de demande de financement
        initial = {"duree_mois": 36, "apport": 0}
        context["dmd_fin_form"] = DemandeFinancementForm(initial=initial)
        
        # ✅ Images du véhicule
        images = self.object.images.all().order_by('ordre', 'date_ajout')
        context["images"] = images
        
        # ✅ Image principale (fallback si pas trouvée)
        image_principal = images.filter(est_principale=True).first()
        if not image_principal and images.exists():
            image_principal = images.first()
        context["image_principal"] = image_principal
        
        return context

class VehiculUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Vehicul
    form_class = VehiculForm
    template_name = "vehicul_templates/vehicul_detail.html"
    
    def get_success_url(self):
        return reverse_lazy("vehicul_app:detail-vehicul", kwargs={"pk": self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Voiture mise à jour avec succès")
        return response
    
    def form_invalid(self, form):
        dashboard = VehiculListView()
        dashboard.request = self.request
        dashboard.kwargs = self.kwargs
        dashboard.object = self.get_object()
        dashboard.object_list = self.get_queryset()
        context = dashboard.get_context_data()
        
        context["vehicul_form"] = form
        context["open_vehicul_modal"] = True
        return self.render_to_response(context)
    

class VehiculDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    model = Vehicul
    template_name = "vehicul_templates/detail_vehicul.html"
    success_url = reverse_lazy("vehicul_app:list-vehicul")
    

# ============================================================
# ✅ PAGE : Liste des images d'un véhicule (avec pagination)
# ============================================================
class VehiculeImageListView(LoginRequiredMixin, ListView):
    model = VehiculeImage
    template_name = "vehicul_templates/vehicul_images.html"
    context_object_name = "images"
    paginate_by = 8  # 8 images par page
    
    def get_queryset(self):
        self.vehicule = get_object_or_404(Vehicul, pk=self.kwargs['pk'])
        return self.vehicule.images.all().order_by('ordre', 'date_ajout')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicul'] = self.vehicule
        print(f"🔍 vehicul.pk = {self.vehicule.pk}")  
        if "vehicul_image_form" not in context:
            context["vehicul_image_form"] = VehiculeImageForm()
        
        return context
    

# ============================================================
# ✅ AJOUT : Ajouter une image (CBV)
# ============================================================
# views.py
@login_required
@require_POST
def ajouter_image(request, pk):
    vehicule = get_object_or_404(Vehicul, pk=pk)
    
    # ✅ Vérification des permissions
    if not (request.user.is_superuser or request.user.role == "directeur"):
        messages.error(request, "Vous n'avez pas la permission d'ajouter des images.")
        return redirect('vehicul_app:detail-vehicul', pk=vehicule.pk)
    
    # ✅ Traitement du formulaire
    form = VehiculeImageForm(request.POST, request.FILES)
    
    if form.is_valid():
        image = form.save(commit=False)
        image.vehicule = vehicule
        image.save()
        
        # ✅ Si c'est l'image principale, désactiver les autres
        if image.est_principale:
            VehiculeImage.objects.filter(
                vehicule=vehicule
            ).exclude(pk=image.pk).update(est_principale=False)
        
        messages.success(request, f"✅ Image ajoutée avec succès !")
    else:
        messages.error(request, f"❌ Erreur dans le formulaire : {form.errors}")
    
    # ✅ Redirection vers la page d'images
    return redirect('vehicul_app:vehicul-images-list', pk=vehicule.pk)
    

# ============================================================
# ✅ SUPPRESSION : Supprimer une image (CBV)
# ============================================================
class VehiculeImageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = VehiculeImage
    template_name = "vehicul_templates/vehicul_image_confirm_delete.html"
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    def get_success_url(self):
        return reverse_lazy('vehicul_app:detail-vehicul', kwargs={'pk': self.object.vehicule.pk})
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Image supprimée avec succès !")
        return response
    

# ============================================================
# ✅ API
# ============================================================


from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicul
from .serializers import VehiculSerializer


class APIVehiculListView(generics.ListAPIView):
    """
    API publique pour récupérer tous les véhicules disponibles.
    Accessible sans authentification.
    """
    queryset = Vehicul.objects.all().select_related('marque').prefetch_related('images')
    serializer_class = VehiculSerializer
    permission_classes = [AllowAny]  # ✅ Tout le monde peut voir le catalogue
    
    # ✅ Filtres et recherche
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    
    # ✅ Champs sur lesquels on peut filtrer
    filterset_fields = [
        'marque__nom',
        'carburant',
        'annee',
        'disponible',
    ]
    
    # ✅ Champs sur lesquels on peut rechercher
    search_fields = [
        'marque__nom',
        'modele',
        'description',
    ]
    
    # ✅ Champs sur lesquels on peut trier
    ordering_fields = [
        'prix',
        'annee',
        'kilometrage',
        'date_ajout',
    ]
    ordering = ['-date_ajout']  # ✅ Tri par défaut


class APIVehiculDetailView(generics.RetrieveAPIView):
    """
    API publique pour récupérer les détails d'un véhicule.
    """
    queryset = Vehicul.objects.all().select_related('marque').prefetch_related('images')
    serializer_class = VehiculSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'