from django.db import models

class Marque(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to="marques/", null=True, blank=True)
    
    def __str__(self):
        return self.nom if self.nom else "Marque sans nom"


class Vehicul(models.Model):
    
    TYPES_CARBURANT_CHOICES = [
        ('essence', "Essence"),
        ("diesel", "Diesel"),
        ("electrique", 'Electrique')
    ]
    
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE, related_name='vehicul')
    modele = models.CharField(max_length=100)
    annee = models.IntegerField()
    stock = models.IntegerField(null=True, blank=True)
    prix = models.DecimalField(max_digits=12, decimal_places=0)
    kilometrage = models.IntegerField()
    carburant = models.CharField(max_length=20, choices=TYPES_CARBURANT_CHOICES, default="essence")
    
    # ========== IMAGE PRINCIPALE (conservée) ==========
    image_principale = models.ImageField(upload_to='vehicules/')
    
    
    disponible = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        marque_nom = self.marque.nom if self.marque else "?"
        modele_nom = self.modele if self.modele else "?"
        return f"{marque_nom} {modele_nom}"


# ============================================================
# ✅ NOUVEAU MODÈLE : IMAGES MULTIPLES POUR VÉHICULE
# ============================================================
class VehiculeImage(models.Model):
    """
    Modèle pour gérer plusieurs images par véhicule.
    Permet une galerie illimitée avec pagination.
    """
    vehicule = models.ForeignKey(
        Vehicul, 
        on_delete=models.CASCADE, 
        related_name='images'  # → vehicule.images.all()
    )
    
    image = models.ImageField(
        upload_to='vehicules_images/%Y/%m/%d/',
        verbose_name="image"
    )
    
    alt_text = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Texte alternatif (SEO)",
        help_text="Description courte de l'image pour l'accessibilité"
    )
    
    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
        help_text="Plus le chiffre est petit, plus l'image est affichée en premier"
    )
    
    est_principale = models.BooleanField(
        default=False,
        verbose_name="Image principale",
        help_text="Cochez si cette image doit être l'image principale du véhicule",
    
    )
    
    date_ajout = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'ajout"
    )
    
    class Meta:
        ordering = ['ordre', 'date_ajout']
        verbose_name = "Image du véhicule"
        verbose_name_plural = "Images des véhicules"
    
    def __str__(self):
        return f"{self.vehicule} - Image {self.ordre}"
    
    
     
    
 
