from django import forms
from .models import Vehicul, Marque


class MarqueForm(forms.ModelForm):
    class Meta:
        model = Marque
        fields = ["nom","logo"]
        widgets = {
            "nom": forms.TextInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir le nom de la marque"}),
            "logo": forms.ClearableFileInput(attrs={"class":"file-input file-input-bordered w -full"}),
        }
        
    def clean_nom(self):
        """Vérifie que le champ nom n'est pas vide"""
        nom = self.cleaned_data.get('nom')
        if not nom or not nom.strip():
            raise forms.ValidationError("Le nom de la marque est obligatoire")
        return nom.strip()
    
class VehiculForm(forms.ModelForm):
    class Meta:
        model = Vehicul
        fields = ["marque","modele", "annee",
                  "prix", "kilometrage", "carburant",
                  "image_principale", "disponible", "description",
                  ]
        
        widgets = {
            "marque":forms.Select(attrs={"class":"select select-bordered w-full"}),
            "modele": forms.TextInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir le modèle"}),
            "annee": forms.NumberInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir l'année"}),
            "prix": forms.NumberInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir le prix"}),
            "kilometrage": forms.NumberInput(attrs={"class":"input input-bordered w-full", "placeholder":"Saisir le kilométrage"}),
            "carburant": forms.Select(attrs={"class":"select select-bordered w-full"}),
            "image_principale": forms.ClearableFileInput(attrs={"class":"file-input file-input-bordered w-full"}),
            "disponible": forms.CheckboxInput(attrs={"class":"checkbox checkbox-info"}),
            "description": forms.Textarea(attrs={"class":"textarea textarea-info w-full", "placeholder":"Saisir la description", "rows": 4}),
            }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
          # Configuration des classes CSS pour chaque type de champ
        config = {
            forms.TextInput: 'input input-bordered w-full',
            forms.Select: 'select select-bordered w-full',
            forms.CheckboxInput: 'checkbox checkbox-info',
            forms.ClearableFileInput: 'file-input file-input-bordered w-full',
            forms.NumberInput: 'input input-bordered w-full',
            forms.Textarea: 'textarea textarea-info w-full',
        }
        
        for field_name, field in self.fields.items():
            # Récupère la classe selon le type du widget
            widget_type = type(field.widget)
            css_class = config.get(widget_type, 'input input-bordered w-full')
            field.widget.attrs['class'] = css_class
            
            # Ajoute un placeholder pour les champs texte
            if widget_type in [forms.TextInput, forms.EmailInput, forms.PasswordInput]:
                field.widget.attrs['placeholder'] = f"Saisir {field.label.lower()}"