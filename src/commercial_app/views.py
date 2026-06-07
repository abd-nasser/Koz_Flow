from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


from django.urls import reverse_lazy
from django.conf import settings

from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from auth_app.models import kozUser
from client_app.views import ClientDetailView
from leads_app.models import Vente, demande_financement
from client_app.models import Maintenance
from commercial_app.models import Offre
from chat_app.models import Message


from auth_app.forms import UserRegisterForm, ChangePasswordForm
from leads_app.forms import GestionFinancementForm
from client_app.forms import MaintenanceForm
from .forms import OffreForm

import logging
logger = logging.getLogger(__name__)



@login_required
def creer_offre(request, demande_id):
    demande = get_object_or_404(demande_financement, id=demande_id)
    
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "Vous n'avez pas l'autorisation de créer une offre.")
        return redirect('leads_app:demande-detail', demande.pk)
    
    if hasattr(demande.client, 'offre'):
        messages.warning(request, "Une offre existe déjà pour ce client.")
        return redirect('commercial_app:offre-detail', demande.client.offre.id)
    
    if request.method == 'POST':
        form = OffreForm(request.POST)
        if form.is_valid():
            offre = form.save(commit=False)
            offre.client = demande.client
            offre.demande_financement = demande
            offre.prix_vehicule = form.cleaned_data['prix_vehicule']
            offre.apport_demande = form.cleaned_data['apport_demande']
            offre.montant_finance = offre.prix_vehicule - offre.apport_demande
            offre.mensualite = (offre.montant_finance * (offre.taux_interet / 100 / 12)) / (1 - (1 + offre.taux_interet / 100 / 12) ** -offre.duree_mois)
            offre.type_offre = "demande"
            offre.statut = "envoyee"
            offre.save()
            
            # ✉️ EMAIL AU CLIENT
            try:
                context_email = {
                    'client': demande.client,
                    'offre_id': offre.id,
                    'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                    'montant_finance': offre.montant_finance,
                    'mensualite': offre.mensualite,
                    'duree_mois': offre.duree_mois,
                    'apport': offre.apport_demande,
                    'date_expiration': offre.date_expiration,
                    'lien_offre': request.build_absolute_uri(f"/client/offres/{offre.id}/"),
                }
                html_message = render_to_string('emails/offres/offre_creee_client.html', context_email)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject="📄 Une offre de financement vous attend - KOZ Services",
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[demande.client.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Erreur envoi email au client: {e}")
            
            messages.success(request, f"Offre créée et envoyée à {demande.client.nom_complet}.")
            
            # Redirection selon le rôle
            if request.user.role == 'commercial':
                return redirect('commercial_app:offre-detail', offre.pk)
            else:
                return redirect('directeur_app:offre-detail', offre.pk)
        else:
            # Formulaire invalide
            template = 'commercial_templates/commercial_demande_detail.html' if request.user.role == 'commercial' else 'directeur_templates/directeur_demande_detail.html'
            return render(request, template, {
                'demande': demande,
                'offre_form': form,
                'gestion_type_fin_form': GestionFinancementForm(instance=demande),
                'open_offre_modal': True
            })
    
    return redirect('leads_app:demande-detail', demande.pk)

@login_required
def accepter_offre(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        messages.warning(request, "Cette offre ne peut pas être acceptée.")
        return redirect('commercial_app:offre-detail', offre.pk)
    
    offre.statut = 'acceptee'
    offre.save()
    
    # Créer la vente associée
   
    vente = Vente.objects.create(
        client=offre.client,
        demande_financement=offre.demande_financement,
        statut='conclue_par_offre_acceptee',
        montant=offre.montant_finance
    )
    
    client = offre.client
    # ✉️ EMAIL AU COMMERCIAL ASSIGNÉ
    commercial = client.assigned_commercial
    if commercial and commercial.email:
        try:
            context_email = {
                'client': client,
                'offre_id': offre.id,
                'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                'montant_finance': offre.montant_finance,
                'date_acceptation': timezone.now(),
                'lien_vente': request.build_absolute_uri(f"/commercial/ventes/{vente.id}/"),
                'lien_client': request.build_absolute_uri(f"/commercial/client/{client.id}/"),
            }
            html_message = render_to_string('emails/offres/offre_acceptee_commercial.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="✅ Un client a accepté son offre de financement - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[commercial.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email au commercial: {e}")
    
    messages.success(request, "Offre acceptée. Vente enregistrée. Le commercial a été notifié.")
    return redirect('commercial_app:offre-detail', offre.pk)

@login_required
def refuser_offre(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        messages.warning(request, "Cette offre ne peut pas être refusée.")
        return redirect('leads_app:offre-detail', offre.pk)
    
    offre.statut = 'refusee'
    offre.save()
    
    # ✉️ Email au commercial
    commercial = offre.client.assigned_commercial
    if commercial and commercial.email:
        try:
            context_email = {
                'client': offre.client,
                'offre_id': offre.id,
                'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Non renseigné",
                'date_refus': timezone.now(),
                'lien_client': request.build_absolute_uri(f"/commercial/client/{offre.client.id}/"),
            }
            html_message = render_to_string('emails/offre_refusee_commercial.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="❌ Un client a refusé son offre - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[commercial.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email au commercial: {e}")
    
    messages.info(request, "Offre refusée. Le commercial a été notifié.")
    return redirect('leads_app:offre-detail', offre.pk)

@login_required
def negocier_offre(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        messages.warning(request, "Seules les offres envoyées peuvent être renégociées.")
        return redirect('leads_app:offre-detail', offre.pk)
    
    # 1️⃣ Changer le statut de l'offre
    offre.statut = 'brouillon'
    offre.save()
    
    # 2️⃣ ✉️ Email au commercial
    commercial = offre.client.assigned_commercial
    if commercial and commercial.email:
        try:
            context_email = {
                'client': offre.client,
                'offre_id': offre.id,
                'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Non renseigné",
                'montant_finance': offre.montant_finance,
                'date_demande': timezone.now(),
                'lien_offre': request.build_absolute_uri(f"/commercial/offre/{offre.id}/modifier/"),
                'lien_client': request.build_absolute_uri(f"/commercial/client/{offre.client.id}/"),
            }
            html_message = render_to_string('emails/offres/offre_negociation_commercial.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="🔄 Demande de renégociation d'offre - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[commercial.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email au commercial: {e}")
    
    # 3️⃣ Message pour le client
    messages.info(request, "Votre demande de renégociation a été envoyée. Votre commercial va étudier votre proposition.")
    
    # 4️⃣ Redirection selon le rôle
    if request.user.role == 'client':
        return redirect('leads_app:offre-detail', offre.pk)
    else:
        return redirect('commercial_app:offre-detail', offre.pk)
    
class CommercialDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    
    template_name = "commercial_templates/commercial.html"
    
    #avec la methode test_func de la class UserPassTestMixin seul un commercial peut acceder à la view 
    def test_func(self):
        return self.request.user.is_staff or self.request.user.role =="commercial"
        #self.request.user designe l'utilisateur qui est connecté
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context["commercial"] = self.request.user
        
        if "user_register_form" not in context:
            context["user_register_form"] = UserRegisterForm()
        
        if 'change_pass_form' not in context:
            context["change_pass_form"] = ChangePasswordForm()
            
        #liste des clients assigné à ce commercial
        clients = self.request.user.clients_assignes.all()
        context['clients'] = clients
        
        # Compter les demandes en cours (requête efficace)
        demandes_en_cours = demande_financement.objects.filter(
            client__in=clients,
            etape="en_cours"
        ).count()
        context['demande_financement_en_cours'] = demandes_en_cours
        
        #Compter les offres 
        offres_acceptees = Offre.objects.filter(
            client__in=clients,
            statut="acceptee"
            
        ).count()
        context["offres_acceptees"] = offres_acceptees
        
        #Maintenance planifié
        maintenance_planifiee = Maintenance.objects.filter(
            client__in=clients,
            statut="planifiee"
        ).count()
        
        context["maintenance_planifiee"] = maintenance_planifiee
        
        #message non lus
        context["total_non_lus"] = sum(c.nb_messages_non_lus for c in context["clients"])
        
        return context

##########################################________________OFFRE_VIEW_________________####################################################
class offreSimpleCreateView(LoginRequiredMixin, CreateView):
    model = Offre
    form_class = OffreForm
    template_name = "clients_templates/client_detail.html"
    success_url = reverse_lazy("client_app:detail-client")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "offre_simple_form" not in context:
            context["offre_simple_form"] = OffreForm()
        return context
    
    def form_valid(self, form):
        client_id = self.kwargs.get("pk")
        client = get_object_or_404(kozUser, id=client_id)
        
        form.instance.client = client
        form.instance.type_offre = "simple"
        form.instance.statut = "envoyee"
        offre = form.save()
        
        # ✉️ EMAIL AU CLIENT
        try:
            context_email = {
                'client': client,
                'offre_id': offre.id,
                'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
                'montant_finance': offre.montant_finance,
                'mensualite': offre.mensualite,
                'duree_mois': offre.duree_mois,
                'apport': offre.apport_demande,
                'date_expiration': offre.date_expiration,
                'lien_offre': self.request.build_absolute_uri(f"/client/offres/{offre.id}/"),
            }
            html_message = render_to_string('emails/offres/simple_offre_cree.client.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="📄 Une offre de financement vous attend - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email au client: {e}")
        
        messages.success(self.request, f"Offre simple créée pour {client.nom_complet}. Un email a été envoyé au client.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        En cas d'erreur dans le formulaire, on rouvre le modal
        avec le formulaire contenant les erreurs
        """
        # Récupère la vue de détail client pour avoir le contexte
        detail_view = ClientDetailView()
        detail_view.request = self.request
        detail_view.kwargs = self.kwargs
        context = detail_view.get_context_data()
        
        # Remplace le formulaire par celui avec les erreurs
        context["offre_simple_form"] = form
        context["open_offre_simple_modal"] = True  # ← Flag pour rouvrir le modal
        
        return self.render_to_response(context)
    
class OffreView(LoginRequiredMixin, ListView):
    model = Offre
    context_object_name = "offres"
    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.role == "commercial":
            return ["partials/offre/partials_offre_list.html" if is_htmx else "commercial_templates/commercial_offre_list.html"]
        
        elif self.request.user.role == "directeur":
            return ["partials/offre/partials_offre_list.html" if is_htmx else "directeur_templates/directeur_offre_list.html"]
        
        return ["partials/offre/partials_offre_list.html" if is_htmx else "clients_templates/clients_offre_list.html"]
    
    def get_queryset(self):
        if self.request.user.role == "directeur":
            queryset = Offre.objects.all()
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |Q(client__email__icontains=q)|
                    Q(vehicule_propose__marque__nom__icontains=q)|
                    Q(vehicule_propose__modele__icontains=q)|
                    Q(vehicule_propose__annee__icontains=q)
                )
            if statut:
                queryset = queryset.filter(statut=statut)
                
            return queryset
            
        elif self.request.user.role == "commercial" or (self.request.user.is_staff and not self.request.user.is_superuser):
            queryset = Offre.objects.filter(client__assigned_commercial=self.request.user).select_related("client")
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |Q(client__email__icontains=q)|
                    Q(vehicule_propose__marque__nom__icontains=q)|
                    Q(vehicule_propose__modele__icontains=q)|
                    Q(vehicule_propose__annee__icontains=q)
                )
            if statut:
                queryset = queryset.filter(statut=statut)
                
            return queryset
        else:
            queryset = Offre.objects.filter(client=self.request.user)
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |Q(client__email__icontains=q)|
                    Q(vehicule_propose__marque__nom__icontains=q)|
                    Q(vehicule_propose__modele__icontains=q)|
                    Q(vehicule_propose__annee__icontains=q)
                )
            if statut:
                queryset = queryset.filter(statut=statut)
                
            return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["STATUTS_OFFRE"] = Offre.STATUTS_OFFRE
        return context
        
class OffreDetailView(LoginRequiredMixin, DetailView):
    model = Offre
    context_object_name = "offre"
    template_name = "commercial_templates/offre_detail.html"
    
######################################___________VENTE/GESTION_View__________________#########################################################""""""

def vente_update_statut(request, pk):
    vente = get_object_or_404(Vente, id=pk)
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut in dict(Vente.STATUT_VENTE).keys():
            vente.statut = nouveau_statut
            vente.save()
            messages.success(request, f"Statut de la vente mis à jour : {vente.get_statut_display()}")
        else:
            messages.error(request, "Statut invalide")
    
    return redirect('commercial_app:vente-list')

class VenteListView(LoginRequiredMixin, ListView):
    model = Vente
    template_name = "commercial_templates/vente_list.html"
    context_object_name = "ventes"
    paginate_by = 20

    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.is_superuser or self.request.user.role  == "directeur":
            return ["partials/vente/partials_vente_list.html" if is_htmx else "directeur_templates/directeur_vente_list.html"]
        return ["partials/vente/partials_vente_list.html" if is_htmx else "commercial_templates/commercial_vente_list.html"]
       
        
    def get_queryset(self):
        # 1. Base queryset selon le rôle
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            queryset = Vente.objects.all()
            
        elif self.request.user.is_staff or self.request.user.role == "commercial":
            queryset = Vente.objects.filter(client__assigned_commercial=self.request.user)
        else:
            return Vente.objects.none()

        # 2. Optimisation
        queryset = queryset.select_related('client', 'demande_financement').order_by('-date_vente')

        # 3. Filtres communs
        statut = self.request.GET.get('statut')
        type_vente = self.request.GET.get('type_vente')
        client_name = self.request.GET.get('client')

        if statut:
            queryset = queryset.filter(statut=statut)
        if type_vente:
            queryset = queryset.filter(type_vente=type_vente)
        if client_name:
            queryset = queryset.filter(client__nom_complet__icontains=client_name)

        return queryset
                

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statut_choices'] = Vente.STATUT_VENTE
        return context

############################################# GESTION_MAINTENANCE_VIEW ##########################################################################

@login_required
def confirmer_maintenance(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id, client=request.user)
    
    if maintenance.statut != 'planifiee':
        messages.warning(request, "Cette maintenance ne peut pas être confirmée.")
        return redirect('commercial_app:maintenance-detail', pk=maintenance.id)
    
    maintenance.statut = 'confirmee'
    maintenance.save()
    
    # ✉️ Email au commercial
    commercial = maintenance.client.assigned_commercial
    if commercial and commercial.email:
        try:
            context_email = {
                'client': maintenance.client,
                'commercial': commercial,
                'maintenance': maintenance,
                'lien_maintenance': request.build_absolute_uri(f"/commercial/maintenance/{maintenance.id}/"),
            }
            html_message = render_to_string('emails/maintenance/maintenance_confirmee_commercial.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="✅ Un client a confirmé sa maintenance - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[commercial.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")
    
    messages.success(request, "Votre maintenance a été confirmée. Un email a été envoyé à votre commercial.")
    return redirect('commercial_app:maintenance-detail', pk=maintenance.id)

    
@login_required
def refuser_maintenance(request, maintenance_id):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id, client=request.user)
    
    if maintenance.statut != 'planifiee':
        messages.warning(request, "Cette maintenance ne peut pas être annulée.")
        return redirect('client_app:maintenance-detail', pk=maintenance.id)
    
    maintenance.statut = 'annulee'
    maintenance.save()
    
    # ✉️ Email au commercial
    commercial = maintenance.client.assigned_commercial
    if commercial and commercial.email:
        try:
            context_email = {
                'client': maintenance.client,
                'commercial': commercial,
                'maintenance': maintenance,
                'lien_maintenance': request.build_absolute_uri(f"/commercial/maintenance/{maintenance.id}/"),
            }
            html_message = render_to_string('emails/maintenance/maintenance_annulee_commercial.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="❌ Un client a annulé sa maintenance - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[commercial.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")
    
    messages.info(request, "Votre maintenance a été annulée. Votre commercial a été notifié.")
    return redirect('client_app:maintenance-list')


def changer_statut_maintenance(request, maintenance_id, nouveau_statut):
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    # Vérifier que l'utilisateur est commercial ou directeur
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "Action non autorisée.")
        return redirect('commercial_app:maintenance-detail', pk=maintenance.id)
    
    statuts_valides = ['en_cours', 'effectuee', 'annulee']
    if nouveau_statut not in statuts_valides:
        messages.error(request, "Statut invalide.")
        return redirect('commercial_app:maintenance-detail', pk=maintenance.id)
    
    maintenance.statut = nouveau_statut
    if nouveau_statut == 'effectuee':
        maintenance.date_derniere = timezone.now().date()
        maintenance.kilometrage_dernier = maintenance.kilometrage_actuel
    maintenance.save()
    
    # ✉️ Email au client
    try:
        context_email = {
            'client': maintenance.client,
            'maintenance': maintenance,
            'nouveau_statut': maintenance.get_statut_display(),
            'lien_maintenance': request.build_absolute_uri(f"/client/maintenance/{maintenance.id}/"),
        }
        
        if nouveau_statut == 'en_cours':
            template = 'emails/maintenance/maintenance_en_cours_client.html'
            sujet = "🔄 Votre maintenance est en cours - KOZ Services"
        elif nouveau_statut == 'effectuee':
            template = 'emails/maintenance/maintenance_effectuee_client.html'
            sujet = "✅ Votre maintenance est terminée - KOZ Services"
        else:
            template = 'emails/maintenance/maintenance_annulee_client.html'
            sujet = "❌ Votre maintenance a été annulée - KOZ Services"
        
        html_message = render_to_string(template, context_email)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=sujet,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[maintenance.client.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur envoi email: {e}")
    
    messages.success(request, f"Maintenance passée en '{maintenance.get_statut_display()}'. Le client a été notifié.")
    return redirect('commercial_app:maintenance-detail', pk=maintenance.id)


#######################################__________________MAINTENANCE_VIEW_______________##################################################
class MaintenanceListView(LoginRequiredMixin, ListView):
    model = Maintenance
    context_object_name = "maintenances"
    
    
    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.role == "directeur" or self.request.user.is_superuser:
            return ["partials/maintenance/partials_maintenance_list.html" if is_htmx else "directeur_templates/directeur_maintenance_list.html"]
        
        if self.request.user.role == "commercial" or self.request.user.is_staff: 
            return ["partials/maintenance/partials_maintenance_list.html" if is_htmx else "commercial_templates/commercial_maintenance_list.html"]
        
        return["partials/maintenance/partials_maintenance_list.html" if is_htmx else 'clients_templates/client_maintenance_list.html']
        
    
    def get_queryset(self):
        #Si commercial : Voir maintenances des ses clients
        if self.request.user.role == "commercial" or (self.request.user.is_staff and not self.request.user.is_superuser):
            queryset = Maintenance.objects.filter(client__assigned_commercial=self.request.user).select_related("client")
            q = self.request.GET.get("q")
            type_maintenance = self.request.GET.get("type_maintenance")
            priorite = self.request.GET.get("priorite")
            origine = self.request.GET.get("origine")
            statut = self.request.GET.get("statut")
            effectue_par = self.request.GET.get("effectue_par")
            
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |
                    Q(marque__icontains=q) |
                    Q(modele__icontains=q)|
                    Q(vehicul__marque__nom__icontains=q)|
                    Q(vehicul__modele__icontains=q)|
                    Q(vehicul__annee__icontains=q)|
                    Q(immatriculation__icontains=q)|
                    Q(notes_client__icontains=q)|
                    Q(notes_technicien__icontains=q)|
                    Q(effectue_par__nom_complet__icontains=q)
                )
            
            if type_maintenance:
                queryset = queryset.filter(type_maintenance=type_maintenance)
            
            if priorite:
                queryset = queryset.filter(priorite=priorite)
            
            if origine:
                queryset = queryset.filter(origine=origine)
            
            if statut:
                queryset = queryset.filter(statut=statut)
            
            if effectue_par:
                queryset = queryset.filter(effectue_par=effectue_par)

            return queryset
            
        
        #Si client: Voir ses maintenance 
        elif self.request.user.role == "client":
            queryset = Maintenance.objects.filter(client=self.request.user)
            q = self.request.GET.get("q")
            type_maintenance = self.request.GET.get("type_maintenance")
            priorite = self.request.GET.get("priorite")
            origine = self.request.GET.get("origine")
            statut = self.request.GET.get("statut")
            effectue_par = self.request.GET.get("effectue_par")
            
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |
                    Q(marque__icontains=q) |
                    Q(modele__icontains=q)|
                    Q(vehicul__marque__nom__icontains=q)|
                    Q(vehicul__modele__icontains=q)|
                    Q(vehicul__annee__icontains=q)|
                    Q(immatriculation__icontains=q)|
                    Q(notes_client__icontains=q)|
                    Q(notes_technicien__icontains=q)|
                    Q(effectue_par__nom_complet__icontains=q)
                )
            
            if type_maintenance:
                queryset = queryset.filter(type_maintenance=type_maintenance)
            
            if priorite:
                queryset = queryset.filter(priorite=priorite)
            
            if origine:
                queryset = queryset.filter(origine=origine)
            
            if statut:
                queryset = queryset.filter(statut=statut)
            
            if effectue_par:
                queryset = queryset.filter(effectue_par=effectue_par)

            return queryset
            

        else:
            queryset = Maintenance.objects.all()
            q = self.request.GET.get("q")
            type_maintenance = self.request.GET.get("type_maintenance")
            priorite = self.request.GET.get("priorite")
            origine = self.request.GET.get("origine")
            statut = self.request.GET.get("statut")
            effectue_par = self.request.GET.get("effectue_par")
            
            if q:
                queryset = queryset.filter(
                    Q(client__nom_complet__icontains=q) |
                    Q(marque__icontains=q) |
                    Q(modele__icontains=q)|
                    Q(vehicul__marque__nom__icontains=q)|
                    Q(vehicul__modele__icontains=q)|
                    Q(vehicul__annee__icontains=q)|
                    Q(immatriculation__icontains=q)|
                    Q(notes_client__icontains=q)|
                    Q(notes_technicien__icontains=q)|
                    Q(effectue_par__nom_complet__icontains=q)
                )
            
            if type_maintenance:
                queryset = queryset.filter(type_maintenance=type_maintenance)
            
            if priorite:
                queryset = queryset.filter(priorite=priorite)
            
            if origine:
                queryset = queryset.filter(origine=origine)
            
            if statut:
                queryset = queryset.filter(statut=statut)
            
            if effectue_par:
                queryset = queryset.filter(effectue_par=effectue_par)

            return queryset
            
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context["maintenance_form"] = MaintenanceForm()
        context["TYPE_CHOICES"] = Maintenance.TYPE_CHOICES
        context["priorite_choices"] = Maintenance.PRIORITE_CHOICES
        context["origine_choices"] = Maintenance.ORIGINE_CHOICES
        context["STATUT_CHOICES"] = Maintenance.STATUT_CHOICES
        return context
    
class MaintenanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = "commercial_templates/maintenance_list.html"
    success_url = reverse_lazy("commercial_app:maintenance-list")

    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']

    def form_valid(self, form):
        messages.success(self.request, "Maintenance ajoutée avec succès.")
        return super().form_valid(form)

class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    model = Maintenance
    context_object_name = "maintenance"
    
    def get_template_names(self):
        is_htmx = self.request.headers.get('HX-Request') == 'true'
        if self.request.user.role == "directeur" or self.request.user.is_superuser:
            return ["partials/maintenance/partials_maintenance_detail.html" if is_htmx else "directeur_templates/directeur_maintenance_detail.html"]
        
        if self.request.user.role == "commercial" or self.request.user.is_staff: 
            return ["partials/maintenance/partials_maintenance_detail.html" if is_htmx else "commercial_templates/commercial_maintenance_detail.html"]
        
        return["partials/maintenance/partials_maintenance_detail.html" if is_htmx else 'clients_templates/client_maintenance_detail.html']

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role in ['commercial', 'directeur']:
            if  "update_maintenance_form" not in context:
                context["update_maintenance_form"] = MaintenanceForm(instance=self.object)
            return context
        
        return context

class MaintenanceUpdateView(LoginRequiredMixin, UserPassesTestMixin,UpdateView):
    model= Maintenance
    template_name = "commercial_templates/maintenance_detail.html"
    form_class = MaintenanceForm
    def get_success_url(self):
        return reverse_lazy ("commercial_app:maintenance-detail", kwargs={"pk":self.object.pk})
    
    
    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']

    def form_valid(self, form):
        messages.success(self.request, "Maintenance MAJ avec succès.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        detail_view = MaintenanceDetailView()
        detail_view.request = self.request
        detail_view.kwargs = self.kwargs
        context = detail_view.get_context_data()
        context["update_maintenance_form"] = form
        context["open_update_maintenance_form"] = True
        return self.render_to_response(context)
      
class MaintenanceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Maintenance
    template_name = "commercial_templates/maintenance_detail.html"
    success_url = reverse_lazy("commercial_app:maintenance-list")

    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Maintenance supprimée.")
        return super().delete(request, *args, **kwargs)


