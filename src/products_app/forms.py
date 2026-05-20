from django import forms 
from .models import CategorieProducts, Products

class CategorieProductsForm(forms.ModelForm):
    class Meta:
        model = CategorieProducts
        fields = ['nom']
        widgets = {
            'nom': forms.TextInput(attrs={"class": "input input-bordered" ,'placeholder': 'Nom de la catégorie'}),
        }

class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['categorie', 'nom', 'prix', 'stock', 'image', 'compatible_avec']
        widgets = {
            'categorie': forms.Select(attrs={"class": "select select-bordered"}),
            'nom': forms.TextInput(attrs={"class": "input input-bordered" ,'placeholder': 'Nom du produit'}),
            'prix': forms.NumberInput(attrs={"class": "input input-bordered" ,'placeholder': 'Prix du produit'}),
            'stock': forms.NumberInput(attrs={"class": "input input-bordered" ,'placeholder': 'Stock disponible'}),
            'image': forms.ClearableFileInput(attrs={"class": "file-input file-input-bordered"}),
            'compatible_avec': forms.Textarea(attrs={'rows': 3, 'class': 'textarea textarea-bordered'}),   
        }