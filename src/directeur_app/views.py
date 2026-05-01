from django.shortcuts import render
from django.views.generic import ListView, DeleteView, DetailView, CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin #pour la connection requise et permission selon le role
from auth_app.forms import UserRegisterForm, ChangePasswordForm

class DirecteurDashboardView(LoginRequiredMixin,UserPassesTestMixin,TemplateView ):
    
    template_name = "directeur_templates/directeur.html"
    
    # test_func est une method qui vient de la classe UserPassTestMixin elle retourne la condition de permissité sur la View
    def test_func(self):
        # Seul le directeur ou superuser peut accéder
        return self.request.user.is_superuser or self.request.user.role == "directeur"
    
    
    # get_context_data est une methode de la class TemplateView permet d'ajouter et de return le context qui accecible depuis le template:
    # avec cette method depuis directeur.htlm on peut acceder au info User qui connecter 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["directeur"] = self.request.user
        context["user_register_form"] = UserRegisterForm()
        if 'change_pass_form' not in context:
            context["change_pass_form"] = ChangePasswordForm()
        return context 
       
    

        
        
    
  
    
