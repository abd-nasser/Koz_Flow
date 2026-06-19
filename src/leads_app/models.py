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
        ('demand_refusee', "Demande Refusé")
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
    ('non_classifie', 'non classifié'),
    ('gestion_de_status', "Gérer l'etat de la vente"),
    ('en_cours', 'En cours'),
    ('conclue', 'Conclue'),
    ('conclue_par_offre_acceptee', 'Conclue par offre acceptée'),
    ('perdue', 'Perdue'),
    ('perdue_par_offre_refusee', 'Perdue par offre refusée'),
]
    
    client = models.ForeignKey('auth_app.kozUser', on_delete=models.CASCADE, related_name='ventes')
    demande_financement = models.OneToOneField('demande_financement', on_delete=models.CASCADE, related_name='vente', null=True, blank=True)
    offre = models.OneToOneField("commercial_app.offre", on_delete=models.CASCADE, related_name='vente', null=True, blank=True)
    
    statut = models.CharField(max_length=70, choices=STATUT_VENTE, default='non_classifie')
    montant = models.DecimalField(max_digits=12, decimal_places=0, help_text="Montant total de la vente")
    date_vente = models.DateTimeField(auto_now_add=True)
    
    @property
    def type_vente(self):
        if self.demande_financement is None :
            return 'cash' if self.statut in ['conclue', 'conclue_par_offre_acceptee'] else 'non_classifie'
        
        demande = self.demande_financement
        if demande.financement_type == 'maison':
            return 'maison'
        if demande.financement_type == 'externe':
            if demande.financement_par == 'fidelis':
                return 'externe_fidelis'
            if demande.financement_par == 'alios':
                return 'externe_alios'
            
        return 'non_classifie'
        
