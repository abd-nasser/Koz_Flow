from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from vehicul_app.models import Vehicul, TypeVehicule
from services_app.models import Services, TypesServices
from products_app.models import Products

def home_page_view(request):
    """
    Affiche la page d'accueil HTML
    C'est une vue Django classique, pas une API
    """
    
    #Récuperer tout les vehicules en vedettes
    vehicules_vedette = Vehicul.objects.filter(est_vedette = True)
    
    
    
    # paginator 1 véhicule par page
    paginator = Paginator(vehicules_vedette, 1)
    page_number = request.GET.get('page', 1)
    vehicules_page = paginator.get_page(page_number)
    ctx = {
        "vehicules": Vehicul.objects.all(),
        "vehicules_vedette": vehicules_vedette,
        "vehicules_page":vehicules_page,
        "total_pages":paginator.num_pages,
        "current_page":page_number,
        "types_vehicule" : TypeVehicule.objects.all(),
        "services_vedette": Services.objects.filter(est_vedette = True),
        "produits_vedette": Products.objects.filter(est_vedette = True, est_disponible = True),
        "nouveaux_produits": Products.objects.filter(est_disponible = True,est_nouveau = True)
    }
    return render(request, "home_templates/home_page.html", ctx)


def vehicules_partial(request):
    """
    Vue HTMX pour charger les véhicules paginés
    """
    vehicules_vedette = Vehicul.objects.filter(est_vedette=True).order_by('date_ajout')
    paginator = Paginator(vehicules_vedette, 1)
    page_number = request.GET.get('page', 1)
    vehicules_page = paginator.get_page(page_number)
    return render(request, "partials/vehiculs/vehicul_vedette_gallery.html", {
            "vehicules_page":vehicules_page,
            "total_page": paginator.num_pages,
            "current_page":page_number
        }
    )
