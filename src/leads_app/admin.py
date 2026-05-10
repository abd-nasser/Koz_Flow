from django.contrib import admin
from .models import demande_financement

@admin.register(demande_financement)
class AdminDemandeFinancement(admin.ModelAdmin):
    list_display = ["client", "Vehicul_interested", "etape", "date_creation"]
