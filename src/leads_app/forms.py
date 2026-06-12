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
            'hx-get':'/leads/estimer-prix/', # URL de la vue qui traite la simulation
            'hx-target': '#resultat-simulation',                # ID de l'élément où afficher le résultat de la simulation
            'hx-trigger': 'change delay:300ms',                   # Déclenche la requête au changement de sélection
            'hx-include': '#simulation-fields',                    # Inclure les champs du formulaire dans la requête HTMX
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
        fields = [
            'cni_passeport',
            'justificatif_domicile',
            'attestation_non_engagement',
            'contrat_travail',
            'attestation_travail',
            'quittance_salaire',      # ← AJOUTER CETTE LIGNE
            'bulletin_1',
            'bulletin_2',
            'bulletin_3',
            'relevé_bancaire',
            'specimen_signature',
            'certificat_presence',
            'geolocalisation',
            'garanties',
            'recu_acompte',
            'fiche_demande',
        ]
        
        widgets = {
            field: forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'})
            for field in fields
        }
    
    def clean(self):
        cleaned_data = super().clean()
        missing_docs = []
        
        # Liste des documents obligatoires
        required_fields = [
            ('cni_passeport', 'CNI / Passeport'),
            ('justificatif_domicile', 'Justificatif de domicile'),
            ('attestation_non_engagement', 'Attestation de non-engagement'),
            ('contrat_travail', 'Contrat de travail'),
            ('attestation_travail', 'Attestation de travail'),
            ('bulletin_1', 'Bulletin de paie -3 mois'),
            ('bulletin_2', 'Bulletin de paie -2 mois'),
            ('bulletin_3', 'Bulletin de paie -1 mois'),
            ('relevé_bancaire', 'Relevé bancaire (12 mois) + RIB'),
            ('specimen_signature', 'Spécimen de signature'),
        ]
        
        for field_name, field_label in required_fields:
            if not cleaned_data.get(field_name):
                missing_docs.append(field_label)
        
        if missing_docs:
            raise forms.ValidationError(
                f"Documents obligatoires manquants : {', '.join(missing_docs)}"
            )
        
        return cleaned_data