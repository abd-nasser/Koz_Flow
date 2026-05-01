# Django a déjà des classes pour gérer les utilisateurs, on va les personnaliser
from django.db import models
from auth_app.models import kozUser


# client_app/models.py

class Maintenance(models.Model):
    
    # ----- TYPES DE MAINTENANCE -----
    TYPE_CHOICES = [
        ('vidange', 'Vidange'),
        ('revision', 'Révision complète'),
        ('pneumatiques', 'Pneumatiques'),
        ('freins', 'Freins/plaquettes'),
        ('climatisation', 'Climatisation'),
        ('batterie', 'Batterie'),
        ('courroie', 'Courroie de distribution'),
        ('autre', 'Autre'),
    ]
    
    # ----- STATUTS -----
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('confirmee', 'Confirmée par client'),
        ('en_cours', 'En cours'),
        ('effectuee', 'Effectuée'),
        ('depassee', 'Dépassée (non faite)'),
        ('annulee', 'Annulée'),
    ]
    
    # ----- PRIORITÉS (pour atelier) -----
    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    # ----- ORIGINE VÉHICULE -----
    ORIGINE_CHOICES = [
        ('koz', 'Acheté chez KOZ'),
        ('externe', 'Véhicule extérieur'),
    ]
    
    # ----- CHAMPS -----
    client = models.ForeignKey(kozUser, on_delete=models.CASCADE, related_name='maintenances', limit_choices_to={'role': 'client'})
    
    # Infos véhicule
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=100)
    annee = models.IntegerField()
    immatriculation = models.CharField(max_length=20)
    kilometrage_actuel = models.IntegerField()
    
    # Origine (remplace le boolean)
    origine = models.CharField(max_length=20, choices=ORIGINE_CHOICES, default='externe')
    
    # Détails maintenance
    type_maintenance = models.CharField(max_length=30, choices=TYPE_CHOICES)
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')
    
    # Dates et kilométrage
    date_prochaine = models.DateField()
    date_derniere = models.DateField(null=True, blank=True)
    kilometrage_prochain = models.IntegerField()
    kilometrage_dernier = models.IntegerField(null=True, blank=True)
    
    # Prix (si payant)
    montant_estime = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    montant_reel = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee')
    
    # Rappels
    rappel_envoye = models.BooleanField(default=False)
    date_rappel = models.DateField(null=True, blank=True)
    sms_envoye = models.BooleanField(default=False)
    email_envoye = models.BooleanField(default=False)
    
    # Notes
    notes_client = models.TextField(blank=True)
    notes_technicien = models.TextField(blank=True)
    
    # Champs techniques
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    effectue_par = models.ForeignKey(kozUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenances_effectuees', limit_choices_to={'role': 'commercial'})
    
    def __str__(self):
        return f"{self.client.nom_complet} - {self.marque} {self.modele} - {self.get_type_maintenance_display()}"
    
    class Meta:
        ordering = ['date_prochaine']
        indexes = [
            models.Index(fields=['statut', 'date_prochaine']),
            models.Index(fields=['origine', 'statut']),
            models.Index(fields=['priorite', 'statut']),
        ]



class Documents(models.Model):
    TYPES_DOCUMENTS = [
        ("cni", "Carte d'identité"),
        ("passeport", 'Passeport'),
        ('justificatif_domicile', 'Justificatif de domicile'),
        ('quittance de salaire', "Quittance de salaire"),
        ("releve_bancaire", "Relevé bancaire"),
        ("contrat_travail", "Contrat de travail"),
        ("autre", "Autre document")
    ]
    
    STATUS = [
        ("en_attente", 'En attente de téléchargement'),
        ("telecharge", "Téléchargé - En cours de verification"),
        ('valide', 'Validé par le commercial'),
        ("rejete", "Rejeté"),
    ]
    
    # Quel koz_user a envoyé ce document ?
    client = models.ForeignKey(kozUser, on_delete=models.CASCADE, related_name="documents", limit_choices_to={'role': 'client'})
    
    # A quelle demande de financement ce document est-il associé ? (peut être null si le client a juste upload un document sans l'associer à une demande)
    demande_financement = models.ForeignKey(
        'leads_app.demande_financement', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Type de document (parmi la liste TYPES_DOCUMENTS)
    type_document = models.CharField(max_length=50, choices=TYPES_DOCUMENTS,)
    
    #Le fichier lui-meme (PDF, image, etc)
    #upload_to='documents/kozUser_id{id}'= dossier organisé par kozUser
    fichier = models.FileField(upload_to='documents/%Y/%m/%d/')
    
    #statut du document
    statut = models.CharField(max_length=30, choices=STATUS, default="en_attente")
    
    #commentaire du commercial
    commentaire_rejet = models.TextField(blank=True, null=True)
    
    #Date d'envoi
    date_upload = models.DateTimeField(auto_now_add=True)
    
    #date de validation
    date_validation = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.client.email}-{self.get_type_document_display()}'
    
    
