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
        ("nouveau_dossier", 'Nouveau dossier'),
        ("en_attente", "en attente de document client"),
        ("dossier_complet", "Dossier complet"),
        ("dossier_accepte", "Dossier Accepté"),
        ('dossier_rejete', "Dossier Refusé")
    ]
    
    # Le client qui a fait la demande
    client = models.ForeignKey(
        kozUser, 
        on_delete=models.SET_NULL, 
        related_name="demande_fin",
        limit_choices_to={"role": "client"},
        null=True,
        blank=True
        )
    
    
    # L'entrepise qui finance la demande
    financement_par = models.CharField(max_length=50, 
                                      choices=[
                                                ("fidelis,", "Fidelis"),
                                                ('Alios', "Alios")
                                                        ],
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
    
    other_Vehicul_interested = models.CharField(null=True, blank=True )
    
    #------3.Financement SIMULATOR()--------------------
    apport = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    duree_mois = models.IntegerField(default=36)
    
    mensualite_simulee = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    
    revenus_mensuel = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    
    #------5.WORKFLOW(where is the dir ?)-------
    etape = models.CharField(max_length=20, choices=ETAPES, default="nouveau")
    
     # À quel utilisateur (commercial) est assigné ?
    assigned_to = models.ForeignKey(
        kozUser, 
        on_delete=models.SET_NULL,
        null=True,
        blank= True,
        related_name='assigned_leads',
        limit_choices_to={'role':'commercial'}
    )
    
    # Qui a fait l'assignation (directeur)
    assigned_by = models.ForeignKey(
        kozUser,  # Changement ici
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads_as_manager',
        limit_choices_to={'role': 'directeur'}
    )
    
    notes_commercial = models.TextField(blank=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        pass