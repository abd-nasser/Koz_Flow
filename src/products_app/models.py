from django.db import models

class CategorieProducts(models.Model):
    nom = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nom if self.nom else "Catégorie sans nom"

class Products(models.Model):
    categorie = models.ForeignKey(CategorieProducts, on_delete=models.CASCADE, related_name="produits")
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=12, decimal_places=0, default=0.0)
    stock = models.IntegerField(default=0)
    image_principale = models.ImageField(upload_to='produits/')
    compatible_avec = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.nom if self.nom else "Produit sans nom"
    
class ProductsImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="images", null=True, blank=True)
    image = models.ImageField(upload_to="products_images/", verbose_name="Image")
    alt_text = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Description courte de l'image pour l'accessibilité"
    )
    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
        help_text="Plus le chiffre est petit, plus l'image est affichée en premier"
    )
    est_principale = models.BooleanField(
        default=False,
        verbose_name="Image Principale",
        help_text="Cochez si cette image doit être l'image principale du produit"
    )
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    class Meta:
        ordering = ["ordre", "date_ajout"]
        verbose_name = "Image du produit"
        verbose_name_plural = "Images des produits"
    
    def __str__(self):
        return f"{self.product} - Image {self.ordre}"