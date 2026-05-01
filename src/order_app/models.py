from django.db import models
from auth_app.models import kozUser
from products_app.models import Products



class Panier(models.Model):
    """Un panier appartient à un client """
    client = models.OneToOneField(kozUser, on_delete=models.CASCADE,related_name="panier")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def total_panier(self):
        return sum(article.sous_total for article in self.articlepanier_set.all())


class ArticlePanier(models.Model):
    """plusieur article ou un article dans le panier"""
    panier = models.ForeignKey(Panier, on_delete=models.SET_NULL, related_name="articles", null=True)
    products = models.ForeignKey(Products, on_delete=models.CASCADE,related_name="dans_panier")
    quantite = models.IntegerField(db_default=1)
    
    
    def sous_total(self):
        return  self.quantite * self.products.prix
    

class Commande(models.Model):
    STATUT_COMMANDE = [
        ("Chargement","Chargement"),
        ("validée", "Validée"),
        ("payee", "Payée"),
        ("livraison", "En livraison"),
        ("terminée", "terminée"),
    ]
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_COMMANDE, default="Chargement")
    date_commande = models.DateTimeField(auto_now_add=True)
    paiements = models.OneToOneField("paiement_app.Paiement", related_name="commande_paiement", on_delete=models.SET_NULL, null=True, blank=True)