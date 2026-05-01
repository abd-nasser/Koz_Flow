from django.shortcuts import render


def login_page(request):
    
    """
    Affiche la page de connexion HTML
    C'est une vue Django classique, pas une API
    """
    return render(request, "auth_templates/login.html")        
