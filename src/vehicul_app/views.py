from django.shortcuts import render
from django.views.generic import CreateView, ListView,DetailView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy 

from .models import Vehicul, Marque
from .forms import VehiculForm, MarqueForm
from directeur_app.views import DirecteurDashboardView


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
    template_name= "vehicul_templates/vehicul_list.html"
    context_object_name ="vehicul_list"
    
    
class VehiculDetailView(LoginRequiredMixin, DetailView):
    model = Vehicul
    template_name = "vehicul_templates/vehicul_detail.html"
    context_object_name = "vehicul"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "vehicul_form" not in context:
            context["vehicul_form"] = VehiculForm(instance=self.object)
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