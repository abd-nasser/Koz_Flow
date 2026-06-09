from django.db import models
from datetime import datetime

class Offre(models.Model):
    #Lien vers client
    client = models.OneToOneField("auth_app.kozUser", on_delete=models.CASCADE, related_name="offre")
    
    demande_financement = models.OneToOneField("leads_app.demande_financement", on_delete=models.CASCADE, related_name="offre", null=True, blank=True)
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
    total_du = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    
    # Statut de l'offre
    STATUTS_OFFRE = [
        ('brouillon', 'En cours de rédaction'),
        ('envoyee', 'Envoyée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('expiree', 'Offre expirée'),
    ]
    TYPE_OFFRE_CHOICES = [
        ('simple', 'Offre simple (sans demande)'),
        ('demande', 'Offre liée à une demande'),
    ]
    statut = models.CharField(max_length=30, choices=STATUTS_OFFRE, default="brouillon")
    type_offre = models.CharField(max_length=20, choices=TYPE_OFFRE_CHOICES, default="simple")  # standard ou simple
    signature_client = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    # Validité de l'offre (ex: 15 jours)
    date_expiration = models.DateTimeField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def save(self,  *args, **kwargs):
        #avant d'enregistrer, on calcule automatiquement le total dû
        self.total_du = (self.mensualite * self.duree_mois) + self.frais_dossier + self.frais_garantie
        # Vérifier si l'offre a expiré
        if self.date_expiration == datetime.now():
            self.statut = 'expiree'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"offre pour {self.client.nom_complet}-{self.statut}"
    