# Django a déjà des classes pour gérer les utilisateurs, on va les personnaliser
from django.db import models
from auth_app.models import kozUser


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
    client = models.ForeignKey(kozUser, on_delete=models.CASCADE, related_name="documents")
    demande_financement = models.ForeignKey('leads_app.demande_financement', on_delete=models.CASCADE, related_name="documents")
    
    # 📌 Documents obligatoires (pour toute demande)
    cni_passeport = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="CNI ou Passeport",)
    justificatif_domicile = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Justificatif de domicile")
    quittance_salaire = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Quittance de salaire")
    relevé_bancaire = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="Relevé bancaire")
    
    # 📌 Documents supplémentaires (optionnels, selon profil)
    contrat_travail = models.FileField(upload_to='documents/%Y/%m/%d/', blank=True, null=True, verbose_name="Contrat de travail")
    avis_imposition = models.FileField(upload_to='documents/%Y/%m/%d/', blank=True, null=True, verbose_name="Avis d'imposition")
    autres = models.FileField(upload_to='documents/%Y/%m/%d/', blank=True, null=True, verbose_name="Autres documents")
    
    # Statut global du dossier de documents
    STATUT_DOCS = [
        ("envoye", "envoyés"),
        ('incomplet', 'Dossier incomplet'),
        ('complet', 'Dossier complet'),
        ('verification', 'En cours de vérification'),
        ('valide', 'Documents validés'),
        ('rejete', 'Documents rejetés'),
    ]
    statut_dossier = models.CharField(max_length=20, choices=STATUT_DOCS, default='envoye')
    
    date_upload = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Dossier {self.client.nom_complet} - {self.statut_dossier}"
    
    def verifier_completude(self):
        """Vérifie si tous les documents obligatoires sont présents"""
        requis = [self.cni_passeport, self.justificatif_domicile, self.quittance_salaire, self.relevé_bancaire]
        if all(requis):
            self.statut_dossier = 'complet'
            self.save()
            return True
        return False