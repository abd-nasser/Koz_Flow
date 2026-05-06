from django.db import models

class Offre(models.Model):
    #Lien vers client
    client = models.OneToOneField("auth_app.kozUser", on_delete=models.CASCADE, related_name="offre")
    
    #La voiture proposée(peut etre différente de celle demandée initialement)
    vehicule_propose =  models.ForeignKey("vehicul_app.vehicul", related_name="offre", on_delete=models.CASCADE)
    
    #Détails du crédit proposé
    prix_vehicule = models.DecimalField(max_digits=12, decimal_places=0)
    apport_demande = models.DecimalField(max_digits=12, decimal_places=0)
    montant_finance = models.DecimalField(max_digits=12, decimal_places=0) #prix - apport
    duree_mois = models.IntegerField()
    mensualite = models.DecimalField(max_digits=12, decimal_places=0)
    taux_interet = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    #frais supplémenatire 
    frais_dossier = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    frais_garantie = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    #total à payer(mensualité * duree + frais)
    total_du = models.DecimalField(max_digits=12, decimal_places=0, blank=True)
    
       # Statut de l'offre
    STATUTS_OFFRE = [
        ('brouillon', 'En cours de rédaction'),
        ('envoyee', 'Envoyée au client'),
        ('acceptee', 'Acceptée par le client'),
        ('refusee', 'Refusée par le client'),
        ('expiree', 'Offre expirée'),
    ]
    
    statut = models.CharField(max_length=30, choices=STATUTS_OFFRE, default="brouillon")
    signature_client = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    # Validité de l'offre (ex: 15 jours)
    date_expiration = models.DateTimeField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def save(self,  *args, **kwargs):
        #avant d'enregistrer, on calcule automatiquement le total dû
        self.total_du = (self.mensualite * self.duree_mois) + self.frais_dossier + self.frais_garantie
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"offre pour {self.client.email}-{self.statut}"
    