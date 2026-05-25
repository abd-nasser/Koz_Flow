from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
from django.db.models import Count, Sum

from django.shortcuts import render

from client_app.models import Documents, Maintenance
from commercial_app.models import Offre
from auth_app.models import kozUser
from leads_app.models import demande_financement


class DashboardView(TemplateView):
    
    template_name = 'dashboard_app/dashboard.html'
    
    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.role == 'directeur' or self.request.user.is_superuser:
            return ['partials/partial_dashboard_directeur.html' if  is_htmx else 'dashboard_templates/directeur_dashboard.html']
        elif self.request.user.role == 'commercial' or self.request.user.is_staff:
            return ['partials/partial_dashboard_commercial.html' if  is_htmx else 'dashboard_templates/commercial_dashboard.html']
        return super().get_template_names()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 📊 KPI Clients
        total_clients = kozUser.objects.filter(role='client').count()
        nb_clients_jour = kozUser.objects.filter(role='client', date_inscription__date=datetime.now().date()).count()
        nb_clients_semaine = kozUser.objects.filter(
            role='client', 
            date_inscription__date__gte=datetime.now().date() - timedelta(days=7)
        ).count()
        
        nb_clients_mois = kozUser.objects.filter(
            role='client', 
            date_inscription__date__gte=datetime.now().date() - timedelta(days=30)
        ).count()

        # Clients avec demande de financement
        clients_avec_demande = kozUser.objects.filter(
            role='client', 
            demande_financement__isnull=False
        ).distinct().count()
        
        # Clients avec offre acceptée
        clients_avec_offre = kozUser.objects.filter(
            role='client', 
            offre__statut='acceptee'
        ).count()
        
        # Taux de conversion (clients → offre acceptée)
        taux_conversion = (clients_avec_offre / total_clients * 100) if total_clients > 0 else 0

        # Top 5 clients (par montant financé)
        top_clients = kozUser.objects.filter(
            role='client', 
            offre__statut='acceptee'
        ).annotate(
            montant_total=Sum('offre__montant_finance')
        ).order_by('-montant_total')[:5]

        context.update({
            'total_clients': total_clients,
            'nb_clients_jour': nb_clients_jour,
            'nb_clients_semaine': nb_clients_semaine,
            'nb_clients_mois': nb_clients_mois,
            'clients_avec_demande': clients_avec_demande,
            'clients_avec_offre': clients_avec_offre,
            'taux_conversion': taux_conversion,
            'top_clients': top_clients,
        })
        
        
        #######################################"" 📊 KPI DEMANDE_FINANCEMENT########################################
        #######################################📊 KPI DEMANDE_FINANCEMENT########################################
        total_demandes = demande_financement.objects.all().count()
        demandes_jour = demande_financement.objects.filter(date_creation__date=datetime.now().date()).count()
        demandes_semaine = demande_financement.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7)).count()
        demandes_mois = demande_financement.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30)).count()
        demandes_accorder_fidelis = demande_financement.objects.filter(etape='accordee_fidelis', financement_type="externe").count()
        demandes_accorder_alios = demande_financement.objects.filter(etape='accordee_alios', financement_type="externe").count()
        demandes_accorder_maison = demande_financement.objects.filter(etape='accordee_maison', financement_type="maison").count()
        demandes_refuser = demande_financement.objects.filter(etape='refusee').count()
        demandes_en_cours = demande_financement.objects.filter(etape='en_cours').count()
        demandes_en_attente = demande_financement.objects.filter(etape='en_attente').count()
        taux_accord_fidelis = ((demandes_accorder_fidelis) / total_demandes * 100) if total_demandes > 0 else 0
        taux_accord_alios = ((demandes_accorder_alios) / total_demandes * 100) if total_demandes > 0 else 0
        taux_accord_externe = ((demandes_accorder_fidelis + demandes_accorder_alios) / total_demandes * 100) if total_demandes > 0 else 0
        taux_accord_maison = ((demandes_accorder_maison) / total_demandes * 100) if total_demandes > 0 else 0

        context.update({
            'total_demandes': total_demandes,
            'demandes_jour': demandes_jour,
            'demandes_semaine': demandes_semaine,
            'demandes_mois': demandes_mois,
            'demandes_accorder_fidelis': demandes_accorder_fidelis,
            'demandes_accorder_alios': demandes_accorder_alios,
            'demandes_accorder_maison': demandes_accorder_maison,
            'demandes_refuser': demandes_refuser,
            'demandes_en_cours': demandes_en_cours,
            'demandes_en_attente': demandes_en_attente,
            'taux_accord_fidelis': taux_accord_fidelis,
            'taux_accord_alios': taux_accord_alios,
            'taux_accord_externe': taux_accord_externe,
            'taux_accord_maison': taux_accord_maison,
        })
        
        
        ############################################"KPI DOCUMENTS"########################################
        ############################################"KPI DOCUMENTS"########################################
        total_dossiers = Documents.objects.all().count()
        dossiers_jour = Documents.objects.filter(date_creation__date=datetime.now().date()).count()
        dossiers_semaine = Documents.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7)).count()
        dossiers_mois = Documents.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30)).count()
        dossier_vide = Documents.objects.filter(statut_dossier='vide').count()
        dossier_incomplet = Documents.objects.filter(statut_dossier='incomplet').count()
        dossier_complet = Documents.objects.filter(statut_dossier='complet').count()
        dossier_en_verification = Documents.objects.filter(statut_dossier='verification').count()
        dossier_rejete = Documents.objects.filter(statut_dossier='rejete').count()
        dossier_valide = Documents.objects.filter(statut_dossier='valide').count()
        taux_dossier_valide = ((dossier_valide) / total_dossiers * 100) if total_dossiers > 0 else 0
        taux_dossier_rejete = ((dossier_rejete) / total_dossiers * 100) if total_dossiers > 0 else 0
        taux_dossier_en_verification = ((dossier_en_verification) / total_dossiers * 100) if total_dossiers > 0 else 0
        context.update({
            'total_dossiers': total_dossiers,
            'dossiers_jour': dossiers_jour,
            'dossiers_semaine': dossiers_semaine,
            'dossiers_mois': dossiers_mois,
            'dossier_vide': dossier_vide,
            'dossier_incomplet': dossier_incomplet,
            'dossier_complet': dossier_complet,
            'dossier_en_verification': dossier_en_verification,
            'dossier_rejete': dossier_rejete,
            'dossier_valide': dossier_valide,
            'taux_dossier_valide': taux_dossier_valide,
            'taux_dossier_rejete': taux_dossier_rejete,
            'taux_dossier_en_verification': taux_dossier_en_verification,
        })
        
        #########################################"KPI OFFRES"########################################
        #########################################"KPI OFFRES"########################################
        total_offres = Offre.objects.all().count()
        offres_jour = Offre.objects.filter(date_creation__date=datetime.now().date()).count()
        offres_semaine = Offre.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7)).count()
        offres_mois = Offre.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30)).count()
        offres_brouillon = Offre.objects.filter(statut='brouillon').count()
        offres_envoyee = Offre.objects.filter(statut='envoyee').count()
        offres_acceptee = Offre.objects.filter(statut='acceptee').count()
        offres_refusee = Offre.objects.filter(statut='refusee').count()
        offres_expiree = Offre.objects.filter(statut='expiree').count()
        taux_offre_acceptee = ((offres_acceptee) / total_offres * 100) if total_offres > 0 else 0
        taux_offre_refusee = ((offres_refusee) / total_offres * 100) if total_offres > 0 else 0
        taux_offre_expiree = ((offres_expiree) / total_offres * 100) if total_offres > 0 else 0
        context.update({
            'total_offres': total_offres,
            'offres_jour': offres_jour,
            'offres_semaine': offres_semaine,
            'offres_mois': offres_mois,
            'offres_brouillon': offres_brouillon,
            'offres_envoyee': offres_envoyee,
            'offres_acceptee': offres_acceptee,
            'offres_refusee': offres_refusee,
            'offres_expiree': offres_expiree,
            'taux_offre_acceptee': taux_offre_acceptee,
            'taux_offre_refusee': taux_offre_refusee,
            'taux_offre_expiree': taux_offre_expiree,
        })
        
        #########################################"""KPI MAINTENANCE"""########################################
        #########################################"""KPI MAINTENANCE"""########################################
        
        total_maintenances = Maintenance.objects.all().count()
        maintenances_jour = Maintenance.objects.filter(date_creation__date=datetime.now().date()).count()
        maintenances_semaine = Maintenance.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=7)).count()
        maintenances_mois = Maintenance.objects.filter(date_creation__date__gte=datetime.now().date() - timedelta(days=30)).count()
        maintenances_effectuee = Maintenance.objects.filter(statut='effectuee').count()
        maintenances_annulee = Maintenance.objects.filter(statut='annulee').count()
        maintenances_acceptee = Maintenance.objects.filter(statut='confirme').count()
        maintenances_planifiee = Maintenance.objects.filter(statut='planifiee').count()
        maintenances_en_cours = Maintenance.objects.filter(statut='en_cours').count()
        taux_maintenance_effectuee = ((maintenances_effectuee) / total_maintenances * 100) if total_maintenances > 0 else 0
        taux_maintenance_annulee = ((maintenances_annulee) / total_maintenances * 100) if total_maintenances > 0 else 0
        taux_maintenance_acceptee = ((maintenances_acceptee) / total_maintenances * 100) if total_maintenances > 0 else 0
        taux_maintenance_planifiee = ((maintenances_planifiee) / total_maintenances * 100) if total_maintenances > 0 else 0
        taux_maintenance_en_cours = ((maintenances_en_cours) / total_maintenances * 100) if total_maintenances > 0 else 0
        context.update({
            'total_maintenances': total_maintenances,
            'maintenances_jour': maintenances_jour,
            'maintenances_semaine': maintenances_semaine,
            'maintenances_mois': maintenances_mois,
            'maintenances_effectuee': maintenances_effectuee,
            'maintenances_annulee': maintenances_annulee,
            'maintenances_acceptee': maintenances_acceptee,
            'maintenances_planifiee': maintenances_planifiee,
            'maintenances_en_cours': maintenances_en_cours,
            'taux_maintenance_effectuee': taux_maintenance_effectuee,
            'taux_maintenance_annulee': taux_maintenance_annulee,
            'taux_maintenance_acceptee': taux_maintenance_acceptee,
            'taux_maintenance_planifiee': taux_maintenance_planifiee,
            'taux_maintenance_en_cours': taux_maintenance_en_cours,
        })



        return context