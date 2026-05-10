from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import DemandeFinancementForm, GestionFinancementForm, DocumentsUploadForm
from .models import DevisLeads, demande_financement
from vehicul_app.models import Vehicul
from client_app.models import Documents

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
def upload_multiple_documents(request, demande_id):
    demande = get_object_or_404(demande_financement, id=demande_id, client=request.user)
    dossier, created = Documents.objects.get_or_create(client=request.user, demande_financement=demande)
    
    if request.method == 'POST':
        form = DocumentsUploadForm(request.POST, request.FILES, instance=dossier)
        if form.is_valid():
            dossier = form.save()
            if dossier.verifier_completude():
                # Option : notifier le commercial
                messages.success(request, "Dossier complet ! Il sera étudié prochainement.")
            else:
                messages.warning(request, "Veuillez uploader tous les documents obligatoires.")
            return redirect('leads_app:detail-demande', demande_id=demande.pk)
    else:  
        return redirect('leads_app:detail-demande', demande_id=demande.pk)

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
    
    return redirect("leads_app:detail-demande", demande_id=demande.pk)




class DemandeFinView(LoginRequiredMixin, ListView):
    model = demande_financement
    context_object_name = "list_demande_financement"

    def get_template_names(self):
        if self.request.user.role == "client":
            return ["clients_templates/client_list_demande.html"]
        if self.request.user.role == "commercial" or self.request.user.is_staff:
            return ["commercial_templates/commercial_list_demande.html"]
        
        return ["directeur_templates/directeur_list_demande.html"]  # fallback

    def get_queryset(self):
        if self.request.user.role == "client":
            return self.request.user.demande_financement.all()
        
        if self.request.user.role == "commercial":
            return demande_financement.objects.filter(
                client__assigned_commercial=self.request.user
            )
        
        # Directeur ou superuser : voit toutes les demandes
        return demande_financement.objects.all()
    
    
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
            dossier, created = Documents.objects.get_or_create(
                client=self.request.user, 
                demande_financement=self.object
            )
            context["upload_doc_form"] = DocumentsUploadForm(instance=dossier)
        
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
        
        

    
    
    
    
        
    
    
