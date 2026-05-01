from django.db import models

class CategorieProducts(models.Model):
    nom = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)

class Products(models.Model):
    categorie = models.ForeignKey(CategorieProducts, on_delete=models.CASCADE, related_name="produits")
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=12, decimal_places=0, default=0.0)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='produits/')
    compatible_avec = models.CharField(max_length=100, blank=True)