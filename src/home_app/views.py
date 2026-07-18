from django.shortcuts import render
from django.views.generic import ListView, DetailView
from vehicul_app.models import Vehicul

def home_page_view(request):
    """
    Affiche la page d'accueil HTML
    C'est une vue Django classique, pas une API
    """
    ctx = {
        "vehicules_vendette": Vehicul.objects.all()
    }
    return render(request, "home_templates/home_page.html", ctx)
     
