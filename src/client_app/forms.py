from django import forms
from .models import Maintenance

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'client',
            'vehicul',               # Si lié au catalogue KOZ
            'marque', 'modele', 'annee', 'immatriculation', 'kilometrage_actuel',
            'origine',
            'type_maintenance',
            'priorite',
            'date_prochaine',
            'date_derniere',
            'kilometrage_prochain',
            'kilometrage_dernier',
            'montant_estime',
            'notes_client',
        ]
        
        widgets = {
            'client': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'vehicul': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'marque': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Ex: Toyota'}),
            'modele': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Ex: Camry'}),
            'annee': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': '2020'}),
            'immatriculation': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'AB-123-CD'}),
            'kilometrage_actuel': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': '45000'}),
            'origine': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'type_maintenance': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'priorite': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'date_prochaine': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
            'date_derniere': forms.DateInput(attrs={'class': 'input input-bordered w-full', 'type': 'date'}),
            'kilometrage_prochain': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': '50000'}),
            'kilometrage_dernier': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': '40000'}),
            'montant_estime': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'placeholder': '75000'}),
            'notes_client': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Si vehicul est séléctionné, on peut pré-remplir marque/modele/annee
        if self.instance and self.instance.vehicul:
            self.fields["marque"].initial = self.instance.vehicul.marque.nom
            self.fields["modele"].initial = self.instance.vehicul.modele
            self.fields["annee"].initial =  self.instance.vehicul.annee
                
    def clean(self):
        cleaned_data = super().clean()
        origine = cleaned_data.get("origine")
        vehicul = cleaned_data.get("vehicul")
        marque = cleaned_data.get("marque")
        modele = cleaned_data.get("modele")
        
        if origine == 'koz' and not vehicul:
            raise forms.ValidationError("Pour un vehicule acheté chez KOZ, Veillez séléctionner le modèle dans la liste")
        
        if origine == "externe" and (not marque or not modele):
            raise forms.ValidationError("Veillez indiquer la marque et le modèle du véhicule.")
        
        return cleaned_data
        
