from django.db import models

class Marque(models.Model):
    nom = models.CharField(max_length=100, null= True, blank=True)
    logo =  models.ImageField(upload_to="marques/",null= True, blank=True)
    
    def __str__(self):
        return self.nom if self.nom else "Marque sans nom"  # ← Fallback
    

class Vehicul(models.Model):
    
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE, related_name='vehicul')
    
    # CharField = texte court pour le nom du modèle (ex: "Clio", "208", "Camry")
    modele = models.CharField(max_length=100)
    
    # IntegerField = nombre entier (ex: 2022 pour l'année)
    annee = models.IntegerField()
    
    prix = models.DecimalField(max_digits=12, decimal_places=0)
    kilometrage = models.IntegerField()
    carburant  = models.CharField(max_length=20, choices=[
        ('essence', "Essence"),
        ("diesel", "Diesel"),
        ("electrique", 'Electrique')
        ])
    
    # ImageField pour la photo principale de la voiture
    image_principale = models.ImageField(upload_to='vehicules/')
    
    disponible = models.BooleanField(default=False)
    description = models.TextField(null=True, blank= True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        marque_nom = self.marque.nom if self.marque else "?"
        modele_nom = self.modele if self.modele else "?"
        return f"{marque_nom} {modele_nom}"
    
 
