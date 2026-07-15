from django.shortcuts import render

def home_page_view(request):
    """
    Affiche la page d'accueil HTML
    C'est une vue Django classique, pas une API
    """
    return render(request, "home_templates/home_page.html")
     
