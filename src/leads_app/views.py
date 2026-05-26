from datetime import timedelta, timezone, datetime

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import DemandeFinancementForm, GestionFinancementForm, DocumentsUploadForm
from commercial_app.forms import OffreForm
from .models import DevisLeads, Vente, demande_financement
from vehicul_app.models import Vehicul
from client_app.models import Documents

##################################################___Demande et Gestion de Financemen_______###########################################
@login_required
def demande_financement_view(request, vehicul_id):
    
    vehicul = get_object_or_404(Vehicul, id=vehicul_id)
    
    if request.user.role != "client":
        messages.error(request, "Seuls les clients peuvent faire une demande.")
        return redirect("vehicul_app:detail-vehicul", vehicul_id=vehicul.id)
    
    # Correction 1 : etape__in
    demande_existante = demande_financement.objects.filter(
        client=request.user,
        etape__in=["brouillon", "envoye", "en_attente", "demande_accorde", "demande_refuse"]
    ).first()
    
    if demande_existante:
        messages.warning(request, f"Cette demande est déjà {demande_existante.etape}.")
        return redirect("client_app:client-view")
    
    if request.method == "POST":
        form = DemandeFinancementForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.client = request.user
            demande.Vehicul_interested = vehicul
            demande.etape = "envoye"
            demande.save()
            messages.success(request, "Votre demande a été envoyée.")
            return redirect("client_app:client-view")
        
            # Erreurs : on rouvre le modal avec le formulaire
        context = {
                'vehicul': vehicul,
                'dmd_fin_form': form,
                'open_dmd_fin_modal': True,
            }
        return render(request, 'vehicul_templates/vehicul_detail.html', context)
   
    return redirect("vehicul_app:detail-vehicul")

@login_required
def attente_document(request, demande_id):
    demande = get_object_or_404(demande_financement, id=demande_id)
    if demande.etape == "en_attente":
        messages.info(request, "cette demande de financement est déjà en attente de document")
    elif demande.etape == "demande_accordee":
        messages.info(request, f"Cette demande de financement est déja accordée par {demande.financement_par if demande.financement_type=="externe" else demande.financement_type}")
    elif demande.etape == "demande_refusee":
        messages.info(request, "cette demande de financement a été réfusée")
    else:
        demande.etape = "en_attente"
        demande.save()
        messages.info(request, "cette demande financement est désormais en attente de document")
        """send_mail(
           subject="",
           message="",
           from_email=Setting,
           recipient_list=[],
           fail_silently=False
           
            
        )
        
        API WHATSAPP à voir apres
        
        """
    return redirect("leads_app:detail-demande", demande.pk)

@login_required
def refuser_demande(request, demande_id):
    demande = get_object_or_404(demande_financement, id=demande_id)
    
    if demande.etape == "demande_refusee":
        messages.info(request, "Cette demande est déjà refusée.")
    elif demande.etape == "demande_accordee":
        messages.warning(request, "Cette demande a déjà été accordée, vous ne pouvez pas la refuser.")
    else:
        demande.etape = "demande_refusee"
        demande.save()
        messages.success(request, f"La demande de {demande.client.nom_complet} a été refusée.")
        
        # Option : notifier le client, envoyer lettre de refus
    
    return redirect("leads_app:detail-demande", demande_id=demande.pk)    

@login_required
def accorder_demande(request, demande_id):
    demande = get_object_or_404(demande_financement, id=demande_id)
    
    if demande.etape == "demande_accordee":
        messages.info(request, "Cette demande est déjà accordée.")
    elif demande.etape == "demande_refusee":
        messages.warning(request, "Cette demande a été refusée, vous ne pouvez pas l'accorder.")
    else:
        demande.etape = "demande_accordee"
        demande.save()
        messages.success(request, f"La demande de {demande.client.nom_complet} a été accordée.")
        
        # Option : notifier le client, générer contrat, etc.
    
    return redirect("leads_app:detail-demande", demande.pk)

@login_required
def estimer_prix_vehicule(request):
    # 1. On récupère les données GET (envoyées par HTMX)
    mensualite = float(request.GET.get('mensualite_souhaitee', 0)) 
    taux_annuel = float(request.GET.get('taux_interet', 8)) / 100  # 8% → 0.08
    duree_mois = int(request.GET.get('duree_mois', 36))
    apport = float(request.GET.get('apport', 0))

    # 2. Si pas de mensualité, on ne calcule rien
    if mensualite <= 0:
        return JsonResponse({'prix_estime': 0})

    # 3. Calcul du capital empruntable
    taux_mensuel = taux_annuel / 12  # ex: 0.08 / 12 = 0.006666
    # Math : C = M * (1 - (1 + t)^(-n)) / t
    try:
        capital = mensualite * (1 - (1 + taux_mensuel) ** -duree_mois) / taux_mensuel
    except:
        capital = 0

    # 4. Prix du véhicule = capital + apport
    prix_vehicule = capital + apport

    # 5. On renvoie le résultat en JSON (HTMX l'affichera)
    return JsonResponse({
        'prix_estime': round(prix_vehicule)
    })
    
class DemandeFinView(LoginRequiredMixin, ListView):
    model = demande_financement
    context_object_name = "list_demande_financement"

    def get_template_names(self):
        is_htmx = self.request.headers.get("HX-Request") == "true"
        
        if self.request.user.role == "client":
            return ["partials/leads/partial_clients_list_demande.html" if is_htmx else "clients_templates/client_list_demande.html"]
        
        if self.request.user.role == "directeur" or self.request.user.is_superuser:
            return ["partials/leads/partial_directeur_list_demande.html" if is_htmx else "directeur_templates/directeur_list_demande.html"]
        
        if self.request.user.role == "commercial" or self.request.user.is_staff:
            return ["partials/leads/partial_commercial_list_demande.html" if is_htmx else "commercial_templates/commercial_list_demande.html"]
        
        # fallback (au cas où)
        return ["partials/leads/partial_clients_list_demande.html" if is_htmx else "clients_templates/client_list_demande.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["etape"] = demande_financement.ETAPES
        context["financement_type_choices"] = demande_financement.FINANCEMENT_TYPE_CHOISE
        context["financement_par_choices"] = demande_financement.ENTREPRISE_FINANCE
        return context

    def get_queryset(self):
        if self.request.user.role == "client":
            queryset = self.request.user.demande_financement.all().select_related("Vehicul_interested", "client")
            
            search_query = self.request.GET.get("q")
            etape = self.request.GET.get("etape")
            financement_type = self.request.GET.get("type_entreprise")
            financement_par = self.request.GET.get("financement_par")
            
            if search_query:
                queryset = queryset.filter(Q(client__nom_complet__icontains=search_query)|
                                           Q(etape__icontains=search_query)|
                                           Q(financement_type__icontains=search_query)|
                                           Q(financement_par__icontains=search_query)|
                                           Q(Vehicul_interested__marque__nom__icontains=search_query)|
                                           Q(Vehicul_interested__modele__icontains=search_query)|
                                           Q(notes_commercial__icontains=search_query)
                                           ).distinct()
            if etape:
                queryset = queryset.filter(etape=etape)
            if financement_type:
                queryset = queryset.filter(financement_type=financement_type)
            if financement_par:
                queryset = queryset.filter(financement_par=financement_par)
                
            return queryset.order_by("-date_creation")
        
        if self.request.user.role == "commercial":
            queryset = demande_financement.objects.filter(
                client__assigned_commercial=self.request.user
            )
            search_query = self.request.GET.get("q")
            etape = self.request.GET.get("etape")
            financement_type = self.request.GET.get("type_entreprise")
            financement_par = self.request.GET.get("financement_par")
            
            if search_query:
                queryset = queryset.filter(Q(client__nom_complet__icontains=search_query)|
                                           Q(etape__icontains=search_query)|
                                           Q(financement_type__icontains=search_query)|
                                           Q(financement_par__icontains=search_query)|
                                           Q(Vehicul_interested__marque__nom__icontains=search_query)|
                                           Q(Vehicul_interested__modele__icontains=search_query)|
                                           Q(notes_commercial__icontains=search_query)
                                           ).distinct()
            if etape:
                queryset = queryset.filter(etape=etape)
            if financement_type:
                queryset = queryset.filter(financement_type=financement_type)
            if financement_par:
                queryset = queryset.filter(financement_par=financement_par)
                
            return queryset.order_by("-date_creation")
        else:
            # Directeur ou superuser : voit toutes les demandes
            queryset = demande_financement.objects.all().select_related("Vehicul_interested", "client").order_by("-date_creation")
            search_query = self.request.GET.get("q")
            etape = self.request.GET.get("etape")
            financement_type = self.request.GET.get("type_entreprise")
            financement_par = self.request.GET.get("financement_par")
                
            if search_query:
                queryset = queryset.filter(Q(client__nom_complet__icontains=search_query)|
                                            Q(etape__icontains=search_query)|
                                            Q(financement_type__icontains=search_query)|
                                            Q(financement_par__icontains=search_query)|
                                            Q(Vehicul_interested__marque__nom__icontains=search_query)|
                                            Q(Vehicul_interested__modele__icontains=search_query)|
                                            Q(notes_commercial__icontains=search_query)
                                            ).distinct()
            if etape:
                queryset = queryset.filter(etape=etape)
            if financement_type:
                queryset = queryset.filter(financement_type=financement_type)
            if financement_par:
                queryset = queryset.filter(financement_par=financement_par)
                    
            return queryset.order_by("-date_creation")
        
        
class DemandeDetailView(LoginRequiredMixin, DetailView):
    model = demande_financement
    context_object_name = "demande" 
    
    def get_template_names(self):
        if self.request.user.role == "client":
            return ["clients_templates/client_demande_detail.html"]
        if self.request.user.role == "commercial" or self.request.user.is_staff:
            return ["commercial_templates/commercial_demande_detail.html"]
        return ["directeur_templates/directeur_demande_detail.html"]  # fallback
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Seul le client peut uploader des documents pour sa propre demande
        if self.request.user.role == "client":
            dossier, created = Documents.objects.get_or_create(client=self.request.user, demande_financement=self.object)
            context["upload_doc_form"] = DocumentsUploadForm(instance=dossier)
            
        if self.request.user.role in ["directeur", "commercial"]:
            initial = {
            'vehicule_propose': self.object.Vehicul_interested,
            'prix_vehicule': self.object.Vehicul_interested.prix if self.object.Vehicul_interested else 0,
            'apport_demande': self.object.apport,
            'duree_mois': self.object.duree_mois,
            'taux_interet': 8.0,  # valeur par défaut
            'frais_dossier': 50000,
            'frais_garantie': 75000,
            'date_expiration': datetime.now()+timedelta(days=30),
             }   
            context["offre_form"] = OffreForm(initial=initial)
            context["gestion_type_fin_form"] = GestionFinancementForm(instance=self.object)
         
        return context
class GestionTypeFinancementView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = demande_financement
    form_class = GestionFinancementForm
  
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff or self.request.user.role =="directeur" or self.request.user.role =="commercial"
    
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role =="directeur":
            return ["directeur_templates/directeur_demande_detail.html"]
        if self.request.user.role == "commercial" or self.request.user.is_staff:
            return ["commercial_templates/commercial_demande_detail.html"]
        
    def get_success_url(self):
        return reverse_lazy("leads_app:detail-demande", kwargs={"pk": self.object.pk})
        



################################################### DOCUMENTS VIEWS #####################################################################
@login_required
def upload_multiple_documents(request, demande_id):
    demande = get_object_or_404(demande_financement, id=demande_id, client=request.user)
    dossier, created = Documents.objects.get_or_create(client=request.user, demande_financement=demande)
    
    if request.method == 'POST':
        form = DocumentsUploadForm(request.POST, request.FILES, instance=dossier)
        if form.is_valid():
            dossier = form.save()
            if dossier.verifier_completude():
                messages.success(request, "Dossier complet ! Il sera étudié prochainement.")
                dossier.demande_financement.etape = "en_cours"
                dossier.demande_financement.save()
            else:
                dossier.statut_dossier = "incomplet"
                dossier.save()
                messages.warning(request, "Veuillez uploader tous les documents obligatoires.")
        else:
            messages.error(request, "Erreur dans l'upload des fichiers.")
    
    return redirect('leads_app:detail-demande', demande.pk)

@login_required
def valide_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    
    if dossier.statut_dossier == "incomplet":
        messages.error(request, "Dossier incomplet, documents obligatoires manquants.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    if dossier.statut_dossier == "rejete":
        messages.warning(request, "Dossier rejeté, ne peut pas être validé.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # 1️⃣ Valider le dossier
    dossier.statut_dossier = "valide"
    dossier.save()
    
    # 2️⃣ Mettre à jour la demande et créer la vente
    demande = dossier.demande_financement
    
    if demande.financement_type == "externe":
        if demande.financement_par == "fidelis":
            demande.etape = "demande_accordee_fidelis"
        elif demande.financement_par == "alios":
            demande.etape = "demande_accordee_alios"
        demande.save()
        
        # ✅ Vente externe conclue
        Vente.objects.create(
            client=demande.client,
            demande_financement=demande,
            statut='conclue',
            montant=demande.montant_souhaite  # ou demande.mensualite_simulee * duree_mois
        )
        
    elif demande.financement_type == "maison":
        # ✅ Vente interne (KOZ Finance) conclue
        demande.etape = "demande_accordee_maison"  # à ajouter dans ETAPES
        demande.save()
        
        Vente.objects.create(
            client=demande.client,
            demande_financement=demande,
            statut='conclue',
            montant=demande.montant_souhaite
        )
    
    messages.success(request, "Dossier validé. Demande et vente enregistrées.")
    return redirect("leads_app:document-detail", dossier.pk)

@login_required
def modifier_dossier (request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id, client=request.user)
    if dossier.statut_dossier == "valide":
        messages.warning(request, "ce dossier a été validé, vous ne pouvez plus le modifier")
    elif dossier.statut_dossier == "rejete":
        messages.warning(request, "ce dossier a été rejeté, vous ne pouvez plus le modifier, veuillez faire une nouvelle demande de financement")
    else:
        dossier.statut_dossier = "modification"
        dossier.save()
        messages.info(request, "les documents de ce dossier sont en attente de modification")
    return redirect("leads_app:document-detail", dossier.pk)
       
@login_required
def rejete_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    demande = dossier.demande_financement
    
    if dossier.statut_dossier == "rejete":
        messages.info(request, "Ce dossier est déjà rejeté.")
    elif dossier.statut_dossier == "valide":
        messages.warning(request, "Ce dossier a été validé, vous ne pouvez pas le rejeter.")
    else:
        # 1️⃣ Rejeter le dossier
        dossier.statut_dossier = "rejete"
        dossier.save()
        
        # 2️⃣ Mettre à jour l'étape de la demande
        demande.etape = "demand_refusee"
        demande.save()
        
        # 3️⃣ Si une vente existait déjà (ex: validé par erreur, puis rejeté ?), on la passe en "perdue"
        if hasattr(demande, 'vente'):
            vente = demande.vente
            vente.statut = 'perdue'
            vente.save()
            messages.info(request, "La vente associée a été marquée comme perdue.")
        
        messages.success(request, "Dossier rejeté. Demande marquée comme refusée.")
    
    return redirect("leads_app:document-detail", dossier.pk)

@login_required
def verifier_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    if dossier.statut_dossier == "verification":
        messages.info(request, "ce dossier est déjà en cours de vérification")
    elif dossier.statut_dossier == "valide":
        messages.warning(request, "ce dossier a été validé, vous ne pouvez pas le mettre en vérification")
    elif dossier.statut_dossier == "rejete":
        messages.warning(request, "ce dossier a été rejeté, vous ne pouvez pas le mettre en vérification")
    else:
        dossier.statut_dossier = "verification"
        dossier.save()
        messages.success(request, "ce dossier est désormais en cours de vérification")
    
    return redirect("leads_app:document-detail", dossier.pk)    


class DocumentListView(LoginRequiredMixin, ListView):
    model = Documents
    context_object_name = "documents"
    def get_template_names(self):
        is_htmx = self.request.headers.get("HX-request") == "true"
        
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return ["partials/dir_list_doc.html" if is_htmx else "directeur_templates/directeur_list_doc.html"]
        
        if self.request.user.is_staff or self.request.user.role == "commercial":
            return ["partials/com_list_doc.html" if is_htmx else "commercial_templates/commercial_list_doc.html"]
        
        return ["clients_templates/client_list_doc.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statut_choices"] = Documents.STATUT_DOCS
        return context
    
    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.role =="directeur": 
            queryset = Documents.objects.all().select_related("client", "demande_financement").order_by("-date_upload")
            
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
            client_name = self.request.GET.get("client_name")
            date_from = self.request.GET.get("date_from")
            date_to = self.request.GET.get("date_to")
            
            if q:
                queryset = queryset.filter(
                                           Q(statut_dossier__icontains=q)|
                                           Q(client__nom_complet__icontains=q)|
                                           Q(demande_financement__Vehicul_interested__marque__nom__icontains=q)|
                                           Q(demande_financement__Vehicul_interested__modele__icontains=q)|
                                           Q(commentaires__icontains=q)|
                                           Q(demande_financement__etape__icontains=q)|
                                           Q(demande_financement__financement_type__icontains=q)|
                                           Q(demande_financement__financement_par__icontains=q)
                                           ).distinct()
           
            if statut:
                queryset = queryset.filter(statut_dossier=statut)
            if client_name:
                queryset = queryset.filter(client__nom_complet__icontains=client_name)
            if date_from:
                queryset = queryset.filter(date_upload__gte=date_from)
            if date_to:
                queryset = queryset.filter(date_upload__lte=date_to)
                
            return queryset
        
        if self.request.user.is_staff or self.request.user.role == "commercial":
            queryset = Documents.objects.filter(client__in = self.request.user.clients_assignes.all()
                                                ).select_related("client", "demande_financement").order_by("-date_upload")
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
            client_name = self.request.GET.get("client_name")
            date_from = self.request.GET.get("date_from")
            date_to = self.request.GET.get("date_to")
            
            if q:
                queryset = queryset.filter(
                                           Q(statut_dossier__icontains=q)|
                                           Q(client__nom_complet__icontains=q)|
                                           Q(demande_financement__Vehicul_interested__marque__nom__icontains=q)|
                                           Q(demande_financement__Vehicul_interested__modele__icontains=q)|
                                           Q(commentaires__icontains=q)|
                                           Q(demande_financement__etape__icontains=q)|
                                           Q(demande_financement__financement_type__icontains=q)|
                                           Q(demande_financement__financement_par__icontains=q)
                                           ).distinct()
           
            if statut:
                queryset = queryset.filter(statut_dossier=statut)
            if client_name:
                queryset = queryset.filter(client__nom_complet__icontains=client_name)
            if date_from:
                queryset = queryset.filter(date_upload__gte=date_from)
            if date_to:
                queryset = queryset.filter(date_upload__lte=date_to)
                
            return queryset
        
        if self.request.user.role == "client":
            queryset = Documents.objects.filter(client=self.request.user).select_related("client", "demande_financement").order_by("-date_upload")
            
            q = self.request.GET.get("q")
            statut = self.request.GET.get("statut")
            client_name = self.request.GET.get("client_name")
            date_from = self.request.GET.get("date_from")
            date_to = self.request.GET.get("date_to")
            
            if q:
                queryset = queryset.filter(
                                           Q(statut_dossier__icontains=q)|
                                           Q(client__nom_complet__icontains=q)|
                                           Q(demande_financement__Vehicul_interested__marque__nom__icontains=q)|
                                           Q(demande_financement__Vehicul_interested__modele__icontains=q)|
                                           Q(commentaires__icontains=q)|
                                           Q(demande_financement__etape__icontains=q)|
                                           Q(demande_financement__financement_type__icontains=q)|
                                           Q(demande_financement__financement_par__icontains=q)
                                           ).distinct()
           
            if statut:
                queryset = queryset.filter(statut_dossier=statut)
            if client_name:
                queryset = queryset.filter(client__nom_complet__icontains=client_name)
            if date_from:
                queryset = queryset.filter(date_upload__gte=date_from)
            if date_to:
                queryset = queryset.filter(date_upload__lte=date_to)
                
            return queryset
        
        return Documents.objects.none()
            
class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Documents
    context_object_name = "document"
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role =="directeur":
            return ["directeur_templates/directeur_detail_doc.html"]
        if self.request.user.role == "commercial" or self.request.user.is_staff:
            return ["commercial_templates/commercial_detail_doc.html"]
        
        return ["clients_templates/client_detail_doc.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == "client": 
            if "update_doc_form" not in context:
                context["update_doc_form"] = DocumentsUploadForm(instance=self.object)
        return context
    
class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Documents
    form_class = DocumentsUploadForm
    template_name = "clients_templates/client_detail_doc.html"
    def get_success_url(self):
        return reverse_lazy("leads_app:document-detail", kwargs={"pk": self.object.pk})  
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Vos documents on on été mise à jour")
        return response
     
    def form_invalid(self, form):
        doc_detail_view = DocumentDetailView()
        doc_detail_view.request = self.request
        doc_detail_view.kwargs = self.kwargs
        context = doc_detail_view.get_context_data()
        context["open_update_doc_modal"]= True
        context["update_doc_form"] = form
        return self.render_to_response(context)
    
class DocumentDeleteView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    def test_func(self):
        doc = self.get_object()
        return doc.statut_dossier == "rejete"
    model = Documents
    template_name = "clients_templates/client_detail.doc.html"
    success_url = reverse_lazy("leads_app:documents-list")
    
        
    

    
    
        
    
    
