from django.contrib import admin
from .models import Marque, Vehicul, VehiculeImage

# ========== INLINE : Images du véhicule ==========
class VehiculeImageInline(admin.TabularInline):
    model = VehiculeImage
    extra = 3
    fields = ['image', 'alt_text', 'ordre', 'est_principale']
    show_change_link = True


@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ['nom', 'id']
    search_fields = ['nom']


@admin.register(Vehicul)
class VehiculAdmin(admin.ModelAdmin):
    list_display = ['marque', 'modele', 'annee', 'prix', 'disponible', 'date_ajout']
    list_filter = ['marque', 'carburant', 'disponible', 'annee']
    search_fields = ['marque__nom', 'modele', 'description']
    readonly_fields = ['date_ajout']
    
    # ✅ Inline : ajoute les images directement dans la page du véhicule
    inlines = [VehiculeImageInline]


@admin.register(VehiculeImage)
class VehiculeImageAdmin(admin.ModelAdmin):
    list_display = ['vehicule', 'image', 'ordre', 'est_principale', 'date_ajout']
    list_filter = ['est_principale', 'vehicule']
    search_fields = ['vehicule__marque__nom', 'vehicule__modele', 'alt_text']
