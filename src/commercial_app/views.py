from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
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
    
    # Vérifier que l'utilisateur a le droit (commercial/directeur)
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "Vous n'avez pas l'autorisation de créer une offre.")
        return redirect('leads_app:demande-detail', demande.pk)
    
    # Vérifier si une offre existe déjà
    if hasattr(demande.client, 'offre'):
        messages.warning(request, "Une offre existe déjà pour ce client.")
        return redirect('commercial_app:offre-detail', offre_id=demande.client.offre.id)
    try:
        if request.method == 'POST':
            form = OffreForm(request.POST)
            if form.is_valid():
                offre = form.save(commit=False)
                offre.client = demande.client
                offre.prix_vehicule = form.cleaned_data['prix_vehicule']
                offre.apport_demande = form.cleaned_data['apport_demande']
                offre.montant_finance = offre.prix_vehicule - offre.apport_demande
                offre.mensualite = (offre.montant_finance * (offre.taux_interet / 100 / 12)) / (1 - (1 + offre.taux_interet / 100 / 12) ** -offre.duree_mois)
                offre.type_offre = "demande"
                offre.save()
                messages.success(request, "Offre créée avec succès.")
                return render(request, 'commercial_templates/commercial_demande_detail.html', {'demande': demande, 
                                                                                               'offre_form': form,
                                                                                               "gestion_type_fin_form": GestionFinancementForm(instance=demande),
                                                                                               "open_offre_modal": True
                                                                                               }) if request.user.role == 'commercial' else render(request, 'directeur_templates/directeur_demande_detail.html', 
                                                                                                {
                                                                                            'demande': demande, 
                                                                                               'offre_form': form,
                                                                                               "gestion_type_fin_form": GestionFinancementForm(instance=demande),
                                                                                               "open_offre_modal": True
                                                                                               })    
                
    except Exception as e:
        logger.error(f"Une erreur est survenue lors de la création de l'offre: {str(e)}")
        messages.error(request, f"Une erreur est survenue lors de la création de l'offre: {str(e)}")

    return redirect("leads_app:detail-demande", demande.pk)
    
@login_required
def accepter_offre(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        messages.warning(request, "Cette offre ne peut pas être acceptée.")
        return redirect('leads_app:offre-detail', offre_id=offre.id)
    
    offre.statut = 'acceptee'
    offre.save()
    
    # Créer la vente associée
    client = offre.client
    Vente.objects.create(
        client=client,
        demande_financement=client.demande_financement,
        statut='conclue_par_offre_acceptee',
        montant=offre.montant_finance
    )
    
    messages.success(request, "Offre acceptée. Vente enregistrée.")
    return redirect('leads_app:offre-detail', offre_id=offre.id)

@login_required
def refuser_offre(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        messages.warning(request, "Cette offre ne peut pas être refusée.")
        return redirect('commercial_app:offre-detail', offre_id=offre.id)
    
    offre.statut = 'refusee'
    offre.save()
    
    # Créer la vente associée (perdue)
    client=offre.client
    Vente.objects.create(
        client=client,
        demande_financement=client.demande_financement,
        statut='perdue_par_offre_refusee',
        montant=offre.montant_finance
    )
    
    messages.info(request, "Offre refusée.")
    return redirect('commercial_app:offre-detail', offre_id=offre.id)

@login_required
def negocier_offre(request, offre_id):
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    if offre.statut != 'envoyee':
        messages.warning(request, "Seules les offres envoyées peuvent être renégociées.")
        return redirect('leads_app:offre-detail', offre_id=offre.id)
    
    # Option 1 : simple notification
    messages.info(request, "Une demande de renégociation a été envoyée à votre commercial.")
    
    # Option 2 : créer une demande de modification (à implémenter)
    # Negociation.objects.create(offre=offre, client=request.user, ...)
    
    # Option 3 : remettre l'offre en brouillon
    offre.statut = 'brouillon'
    offre.save()
    messages.info(request, "L'offre a été remise en brouillon. Votre commercial peut la modifier.")
    
    return redirect('commercial_app:offre-detail', offre_id=offre.id)

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
        client = self.request.user.clients_assignes.all()
        context['clients'] = client 
        context["total_non_lus"] = sum(c.nb_messages_non_lus for c in context["clients"])
        
        return context


##########################################________________OFFRE_VIEW_________________####################################################
class offreSimpleCreateView(LoginRequiredMixin, CreateView):
    model = Offre
    form_class = OffreForm
    template_name = "clients_templates/client_detail.html"
    
    def get_success_url(self):
        return reverse_lazy('client_app:client-detail', kwargs={'pk': self.kwargs.get('pk')})
    
    def form_valid(self, form):
        client_id = self.kwargs.get("pk")
        client = get_object_or_404(kozUser, id=client_id)
        form.instance.client = client
        form.instance.type_offre = "simple"
        form.save()
        messages.success(self.request, f"Offre simple créée pour {client.nom_complet}")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        detail_view = ClientDetailView()
        detail_view.request = self.request
        detail_view.kwargs = self.kwargs
        context = detail_view.get_context_data()
        context["offre_simple_form"] = form
        context["open_offre_simple_modal"] = True
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
        context["type_maintenance_choices"] = Maintenance.TYPE_CHOICES
        context["priorite_choices"] = Maintenance.PRIORITE_CHOICES
        context["origine_choices"] = Maintenance.ORIGINE_CHOICES
        context["statut_choices"] = Maintenance.STATUT_CHOICES
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

class MaintenanceDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Maintenance
    template_name = "commercial_templates/maintenance_detail.html"
    context_object_name = "maintenance"

    def test_func(self):
        return self.request.user.role in ['commercial', 'directeur']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if  "update_maintenance_form" not in context:
            context["update_maintenance_form"] = MaintenanceForm(instance=self.object)
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

############################################# GESTION_MAINTENANCE_VIEW ###################################################################
