# leads_app/forms.py
from django import forms
from .models import demande_financement
from client_app.models import Documents


##POUR LE CLIENT
class DemandeFinancementForm(forms.ModelForm):
    #champs pour simulateur de credit 
    mensualite_souhaitee = forms.DecimalField(
        max_digits=12,
        decimal_places=0,
        required=False,
        label="💸 Mensualité souhaitée (FCFA)",
        widget=forms.NumberInput(attrs={
            "class": "input input-bordered w-full",
            'placeholder': 'Entrez la mensualité souhaitée (FCFA)',
            'hx-get':'/leads/estimer-prix/',                    #URL de la vue qui traite la simulation
            'hx-target': '#resultat-simulation',                #ID de l'élément où afficher le résultat de la simulation
            'hx-trigger': 'keyup changed delay:300ms',          #Déclenche la requête après 300ms de pause dans la saisie
            'hx-include': "#simulation-fields" ,                 #Inclure les champs du formulaire dans la requête HTMX
        })
    )
    
    taux_interet = forms.ChoiceField(
        choices = [(i, f"{i}%") for i in range(0, 18)],  # Taux d'intérêt de 0% à 17%
        required=False,
        initial=8,  # Taux d'intérêt par défaut (exemple : 8%)
        label="📈 Taux d'intérêt annuel (%)",
        widget=forms.Select(attrs={
            "class": "select select-bordered w-full",
            'hx-get':'/leads/estimer-prix/', #URL de la vue qui traite la simulation
            'hx-target': '#resultat-simulation',                #ID de l'élément où afficher le résultat de la simulation
            'hx-trigger': 'changed',                             #Déclenche la requête lors du changement de sélection
            'hx-include': "#simulation-fields"                  #Inclure les champs du formulaire dans la requête HTMX
        })
    )
    
    
    class Meta:
        model = demande_financement
        fields = [
            'apport',
            'duree_mois',
            'revenus_mensuel',
            
        ]
        widgets = {
            'apport': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': 10000,
                'placeholder': 'Montant de l’apport (FCFA)'
            }),
            'duree_mois': forms.Select(choices=[
                (12, '12 mois'),
                (24, '24 mois'),
                (36, '36 mois'),
                (48, '48 mois'),
                (60, '60 mois'),
            ], attrs={'class': 'select select-bordered w-full'}),
            
            'revenus_mensuel': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'step': 50000,
                'placeholder': 'Revenus mensuels (FCFA)'
            }),
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    
    def clean(self):
        cleaned_data = super().clean()
        apport = cleaned_data.get('apport')
        revenus = cleaned_data.get('revenus_mensuel')

        if apport is None or apport <= 0:
            raise forms.ValidationError("L'apport ne peut pas être négatif.")
        if revenus is  None or revenus <= 0:
            raise forms.ValidationError("Les revenus ne peuvent pas être négatifs")
        return cleaned_data


#POUR LE COMMERCIAL
class GestionFinancementForm(forms.ModelForm):
    class Meta:
        model = demande_financement
        fields = [
            "financement_type","financement_par",
            "notes_commercial", 
        ]  
                
        widgets= {
            "financement_type":forms.Select(attrs={"class":"select select-bordered"}),
            "financement_par": forms.Select(attrs={"class":"select select-bordered"}),
            "notes_commercial":forms.Textarea(attrs={"class":"input input-bordered"}),
            
        }

class DocumentsUploadForm(forms.ModelForm):
    class Meta:
        model = Documents
        fields = ['cni_passeport', 'justificatif_domicile', 'quittance_salaire', 'relevé_bancaire', 
                  'contrat_travail', 'avis_imposition', 'autres']
        widgets = {
            field: forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'})
            for field in fields
        }