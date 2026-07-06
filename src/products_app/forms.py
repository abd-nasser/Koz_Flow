from django import forms 
from .models import CategorieProducts, Products, ProductsImage

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
        fields = ['categorie', 'nom', 'prix', 'stock', 'image_principale', 'compatible_avec']
        widgets = {
            'categorie': forms.Select(attrs={"class": "select select-bordered"}),
            'nom': forms.TextInput(attrs={"class": "input input-bordered" ,'placeholder': 'Nom du produit'}),
            'prix': forms.NumberInput(attrs={"class": "input input-bordered" ,'placeholder': 'Prix du produit'}),
            'stock': forms.NumberInput(attrs={"class": "input input-bordered" ,'placeholder': 'Stock disponible'}),
            'image_principale': forms.ClearableFileInput(attrs={"class": "file-input file-input-bordered"}),
            'compatible_avec': forms.Textarea(attrs={'rows': 3, 'class': 'textarea textarea-bordered'}),   
        }
        
#=======================================================================================================
#✅ NOUVEAU : Formulaire pour les images du produits
#=======================================================================================================

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductsImage
        fields = ["image", "alt_text", "ordre", "est_principale"]
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'alt_text': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Description de l\'image (SEO)'}),
            'ordre': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': 0}),
            'est_principale': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }
        