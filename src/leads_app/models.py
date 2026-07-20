from django.db import models
from vehicul_app.models import Vehicul
from auth_app.models import kozUser

class DevisLeads(models.Model):
    """ 
        TABLE WHO STOCK QUOTE REQUEST
    """
    #--- client Infos---
    
    #complet name(required)
    first_name = models.CharField(max_length=100)
    last_name =  models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    
    #---Vehicul Infos---
    Vehicul_interested_in_catalogue = models.ForeignKey(Vehicul, on_delete=models.SET_NULL, related_name="Vehicul_interested", null=True)
    other_Vehicul_interested = models.CharField(null=True,blank=True )
    
    traited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
   
    def __str__(self):
        return f"{self.first_name}-{self.last_name} ({self.phone})"

class demande_financement(models.Model):
    """
        TABLE WHO STOCK REQUEST Financement
    """
    ETAPES = [
        ("nouvelle", "Nouvelle demande de financement"),
        ("en_attente", "en attente de document"),
        ("en_cours", "En cours de traitement"),
        ("demande_accordee_fidelis", "Demande accordée chez Fidelis"),
        ("demande_accordee_alios", "Demande accordée chez Alios"),
        ("demande_accordee_maison", "Demande accordée (KOZ Finance)"),
        ('demande_refusee', "Demande Refusé")
    ]
    
    FINANCEMENT_TYPE_CHOISE = [
        ("maison", "Maison"),
        ("externe", "Externe")
    ]
    
    ENTREPRISE_FINANCE = [
                            ("fidelis", "Fidelis"),
                            ('alios', "Alios")
                                    ]
    
    # Le client qui a fait la demande
    client = models.ForeignKey(
        kozUser, 
        on_delete=models.SET_NULL, 
        related_name="demande_financement",
        limit_choices_to={"role": "client"},
        null=True,
        blank=True
        )
    
    
    financement_type = models.CharField(
        max_length=50, 
        choices=FINANCEMENT_TYPE_CHOISE, 
        null=True, 
        blank=True)
    
    # L'entrepise qui finance la demande
    financement_par = models.CharField(
        max_length=50, 
        choices=ENTREPRISE_FINANCE,
        null=True, blank=True
                                      )
    
    #-----2. THE CAR WANTS(link to the catalogue)

    Vehicul_interested = models.ForeignKey(
        Vehicul, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='demande_financement',
        verbose_name="Véhicule d'intérêt"
        )
    
    other_Vehicul_interested = models.CharField(null=True, blank=True)
    
    #------3.Financement SIMULATOR()--------------------
    apport = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    duree_mois = models.IntegerField(default=36)
    
    mensualite_simulee = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    
    revenus_mensuel = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    
    #------5.WORKFLOW(where is the dir ?)-------
    etape = models.CharField(max_length=100, choices=ETAPES, default="nouvelle")
    
    
    notes_commercial = models.TextField(blank=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client}"
    
# leads_app/models.py

class Vente(models.Model):
    """Vente conclue ou perdue, liée à une demande de financement et un client"""
    
    STATUT_VENTE = [
        ('non_classifie', 'Non classifié'),
        ('gestion_de_status', "Gérer l'état de la vente"),
        ('en_cours', 'En cours'),
        ('conclue', 'Conclue'),
        ('conclue_par_acceptation_offre_simple', "Conclue par acceptation d'offre simple"),
        ('conclue_par_acceptation_offre_financement', "Conclue par acceptation d'offre financement"),
        ('perdue', 'Perdue'),
        ('perdue_par_refus_offre_simple', "Perdue par refus d'offre simple"),
        ('perdue_par_refus_offre_financement', "Perdue par refus d'offre financement"),
        ('perdue_par_rejet_dossier_offre_financement', 'Perdue par rejet de dossier (offre de financement)'),
        ('perdue_par_rejet_dossier_demande_financement', 'Perdue par rejet de dossier (demande de financement)')
    ]
    
    client = models.ForeignKey('auth_app.kozUser', on_delete=models.CASCADE, related_name='ventes')
    demande_financement = models.OneToOneField(
        'demande_financement', 
        on_delete=models.CASCADE, 
        related_name='vente', 
        null=True, 
        blank=True
    )
    offre_financement = models.OneToOneField(
        "commercial_app.offre", 
        on_delete=models.CASCADE, 
        related_name='vente', 
        null=True, 
        blank=True
    )
    
    statut = models.CharField(max_length=70, choices=STATUT_VENTE, default='non_classifie')
    montant = models.DecimalField(max_digits=12, decimal_places=0, help_text="Montant total de la vente")
    date_vente = models.DateTimeField(auto_now_add=True)
    
    @property
    def type_vente(self):
        """
        Détermine le type de vente pour l'analytics :
        - cash : Offre simple acceptée
        - maison : Financement KOZ
        - externe_fidelis : Financement Fidelis
        - externe_alios : Financement Alios
        - non_classifie : Non déterminé
        """
        offre = self.offre_financement
        demande = self.demande_financement
        
        # ✅ CAS 1 : Vente cash (offre simple)
        if offre and offre.type_offre == "simple":
            if self.statut in ['conclue', 'conclue_par_acceptation_offre_simple']:
                return 'cash'
            return 'non_classifie'
        
        # ✅ CAS 2 : Financement maison (KOZ)
        if offre and offre.financement_type == 'maison':
            return 'maison'
        if demande and demande.financement_type == 'maison':
            return 'maison'
        
        # ✅ CAS 3 : Financement externe
        if offre and offre.financement_type == 'externe':
            if offre.financement_par == 'fidelis':
                return 'externe_fidelis'
            if offre.financement_par == 'alios':
                return 'externe_alios'
        
        if demande and demande.financement_type == 'externe':
            if demande.financement_par == 'fidelis':
                return 'externe_fidelis'
            if demande.financement_par == 'alios':
                return 'externe_alios'
        
        return 'non_classifie'
    
    def __str__(self):
        return f"Vente {self.id} - {self.client.nom_complet} - {self.statut}"