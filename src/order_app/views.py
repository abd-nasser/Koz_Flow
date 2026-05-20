from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Panier, ArticlePanier, Commande
from products_app.models import Products, CategorieProducts
from .serializers import PanierSerializer, ArticlePanierSerializer, CommandeSerializer


# ============================================================
# 1. Voir le panier (GET)
# ============================================================

class PanierDetailView(APIView):
    """Retourne le panier complet du user connecté
          GET /api/order/panier/
    """
    permission_classes = [IsAuthenticated] # Seulement les clients connectés
    
    def get(self, request):
        #on récupère ou on cree le panier
        panier, created = Panier.objects.get_or_create(client=request.user)
        
        #serialise le panier(convertit en json)
        serializer = PanierSerializer(panier)

        #retourne la reponse avec le panier(convertit en JSON)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AjouterPanierView(APIView):
    """Ajoute un produit au panier ,
        Augmente la quantité si le produit exite déja 
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        quantite = request.data.get("quantite", 1)
        
        # Vérifie que le produit existe
        product = get_object_or_404(Products, id=product_id)
        
        #recupère le panier ou le cree
        panier, created = Panier.objects.get_or_create(client=request.user)
        
        #Vérifie si l'article est déja dans le panier
        article, created= ArticlePanier.objects.get_or_create(panier=panier,
                                                              products=product,
                                                              defaults={'quantite': quantite})
        
        # Si l'article existait déjà, on augmente la quantité
        if not created:
            article.quantite += quantite
            article.save()
        
        # Retourne le panier mis à jour
        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================
# 3. Modifier la quantité d'un article (PUT)
# ============================================================
class ModifierArticlePanierView(APIView):
    """ 
    Modifier la quantité d'un article dans le panier
    PUT /api/order/panier/modifier/<article_id>/
    body: {"quantite":5}
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, article_id):
        # Récupère l'article (en vérifiant qu'il appartient au client connecté)
        article = get_object_or_404(
            ArticlePanier,
            id=article_id,
            panier__client = request.user
        )
        
        # Récupère la nouvelle quantité
        quantite = request.data.get("quantite")
    
        if quantite is not None and int(quantite) > 0:
            # Mise à jour de la quantité
            article.quantite = int(quantite)
            article.save()
        else:
            # Si quantité = 0, on supprime l'article
            article.delete()
            
        # Retourne le panier mis à jour
        panier = article.panier if quantite > 0 else Panier.objects.get(client=request.user)
        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ============================================================
# 4. Supprimer un article du panier (DELETE)
# ============================================================

class RetirerArticlePAnierView(APIView):
    """
    Supprime un article spécifique du panier.
    DELETE /api/order/panier/retirer/<article_id>/
    """
    def delete(self, request, article_id):
        # Récupère l'article (en vérifiant qu'il appartient au client)
        article = get_object_or_404(
            ArticlePanier,
            id=article_id,
            panier__client=request.user
        )
        
        #Supprime l'article
        panier = article.panier
        article.delete()
        
        # Retourne le panier mis à jour
        serializer = PanierSerializer(panier)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ============================================================
# 5. Vider tout le panier (DELETE)
# ============================================================
class ViderPanierView(APIView):
    """
    Supprime tous les articles du panier.
    DELETE /api/order/panier/vider/
    """
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        # Récupère le panier du client
        panier = Panier.objects.get_or_create(client=request.user)
        
        # Supprime tous les articles
        panier.articles.all().delete()
        
        # Retourne un statut 204 (No Content)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        
    

# ============================================================
# 1. Valider une commande (POST)
# ============================================================ 

class ValiderCommandeView(APIView):
    permission_classes = [IsAuthenticated]
    
    # 1. Vérifier que la commande existe ET appartient au client
    def post(self, request, commande_id):
        commande = get_object_or_404(
            Commande, 
            id=commande_id,
            panier__client=request.user,
            
            )
        # 2. Vérifier que la commande n'est pas déjà traitée
        if commande.statut in  ["validee", "payee", "livraison"]:
            return Response({"error": 'Commande déjà validée ou payée'}, 
                            status=status.HTTP_400_BAD_REQUEST
                            )
        
        # 3. Vérifier que le panier n'est pas vide
        if commande.panier.articles.count() == 0:
            return Response({"error": 'Panier vide'}, 
                            status=status.HTTP_400_BAD_REQUEST
                            )
            
        # 4. Valider la commande
        commande.statut = "validee"
        commande.save() 
        
         # 5. Retourner la commande mise à jour
        serializer = CommandeSerializer(commande)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        