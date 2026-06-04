from datetime import timedelta, timezone, datetime

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.urls import reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import DemandeFinancementForm, GestionFinancementForm, DocumentsUploadForm
from commercial_app.forms import OffreForm
from .models import DevisLeads, Vente, demande_financement
from vehicul_app.models import Vehicul
from client_app.models import Documents

##################################################___Demande et Gestion de Financement_______###########################################
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
            
            # ✉️ ENVOI DE L'EMAIL DE CONFIRMATION
           

            # Vérifier que le client a bien un commercial assigné
            if client.assigned_commercial and client.assigned_commercial.email:
                try:
                    html_message = render_to_string('emails/demande_financement/demande_financement_envoyee.html', context_email)
                    plain_message = strip_tags(html_message)
                    client = request.user
                    
                    context_email = {
                    'client': request.user,
                    'vehicule': f"{vehicul.marque.nom} {vehicul.modele} ({vehicul.annee})",
                    'apport': form.cleaned_data.get('apport', 0),
                    'duree': form.cleaned_data.get('duree_mois', 36),
                    'revenus': form.cleaned_data.get('revenus_mensuel', 0),
                    'lien_suivi': request.build_absolute_uri("/client/demandes/"),
                }
                    send_mail(
                        subject="🆕 Nouvelle demande de financement - KOZ Services",
                        message=plain_message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[client.assigned_commercial.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    messages.info(request, "Votre commercial a été notifié de votre demande.")
                except Exception as e:
                    print(f"Erreur envoi email au commercial: {e}")
            else:
                print(f"Client {client.email} n'a pas de commercial assigné")
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
                # ✉️ Email au client
        try:
            context_email = {
                'client': demande.client,
                'demande_id': demande.id,
                'lien_upload': request.build_absolute_uri(f"/client/documents/upload/{demande.id}/"),
            }
            html_message = render_to_string('emails/demande_financement/demande_attente_documents.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="📎 Documents requis pour votre demande de financement - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[demande.client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")
        
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
        messages.success(request, f"La demande de {demande.client.nom_complet} a été refusée. Un email a été envoyé au client.")
        
        # ✉️ Email au client
        try:
            context_email = {
                'client': demande.client,
                'demande_id': demande.id,
                'raison': request.POST.get('raison_refus', 'Non conforme aux critères de financement'),
            }
            html_message = render_to_string('emails/demande_financement/demande_refusee.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="❌ Mise à jour de votre demande de financement - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[demande.client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")
        
        
        
    
    return redirect("leads_app:detail-demande", demande_id=demande.pk)    

@login_required
def accorder_demande(request, demande_id):
    demande = get_object_or_404(demande_financement, id=demande_id)
    
    if demande.etape == "demande_accordee":
        messages.info(request, "Cette demande est déjà accordée.")
    
    elif demande.etape == "demande_refusee":
        messages.warning(request, "Cette demande a été refusée, vous ne pouvez pas l'accorder.")
    
    else:
        # Déterminer le type d'accord
        if demande.financement_type == "externe" and demande.financement_par == "fidelis":
            demande.etape = "demande_accordee_fidelis"
            partenaire = "Fidelis"
        elif demande.financement_type == "externe" and demande.financement_par == "alios":
            demande.etape = "demande_accordee_alios"
            partenaire = "Alios"
        else:
            demande.etape = "demande_accordee"
            partenaire = "KOZ Finance"
        
        demande.save()
        
        # ✉️ Email au client
        try:
            context_email = {
                'client': demande.client,
                'demande_id': demande.id,
                'partenaire': partenaire,
                'vehicule': str(demande.Vehicul_interested) if demande.Vehicul_interested else "Véhicule sélectionné",
                'lien_offre': request.build_absolute_uri(f"/client/offres/{demande.id}/"),
            }
            html_message = render_to_string('emails/demande_financement/demande_accordee.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="✅ Félicitations ! Votre demande de financement a été acceptée - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[demande.client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email: {e}")
        
        messages.success(request, f"La demande de {demande.client.nom_complet} a été accordée ({partenaire}). Un email a été envoyé au client.")
    
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

    # 5. On renvoie le résultat HTML partiel pour HTMX
    return render(request, "partials/leads/resulta_simulation.html", {"prix_estime": prix_vehicule})

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
                # ✅ Dossier complet
                dossier.statut_dossier = "complet"
                dossier.save()
                demande.etape = "en_cours"
                demande.save()
                
                messages.success(request, "Dossier complet ! Il sera étudié prochainement.")
                
                # ✉️ Email au commercial assigné
                if demande.client.assigned_commercial and demande.client.assigned_commercial.email:
                    try:
                        context_email = {
                            'client': demande.client,
                            'demande_id': demande.id,
                            'vehicule': str(demande.Vehicul_interested) if demande.Vehicul_interested else "Non renseigné",
                            'lien_demande': request.build_absolute_uri(f"/commercial/demande/{demande.id}/"),
                        }
                        html_message = render_to_string('emails/documents/dossier_complet_commercial.html', context_email)
                        plain_message = strip_tags(html_message)
                        
                        send_mail(
                            subject="📄 Dossier complet à étudier - KOZ Services",
                            message=plain_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[demande.client.assigned_commercial.email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                    except Exception as e:
                        print(f"Erreur envoi email au commercial: {e}")
                
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
            partenaire = "Fidelis"
        elif demande.financement_par == "alios":
            demande.etape = "demande_accordee_alios"
            partenaire = "Alios"
        demande.save()
        
        Vente.objects.create(
            client=demande.client,
            demande_financement=demande,
            statut='conclue',
            montant=demande.montant_souhaite
        )
        
    elif demande.financement_type == "maison":
        demande.etape = "demande_accordee_maison"
        demande.save()
        partenaire = "KOZ Finance"
        
        Vente.objects.create(
            client=demande.client,
            demande_financement=demande,
            statut='conclue',
            montant=demande.montant_souhaite
        )
    
    # ✉️ Email au client pour l'informer de l'accord
    try:
        context_email = {
            'client': demande.client,
            'demande_id': demande.id,
            'partenaire': partenaire,
            'vehicule': str(demande.Vehicul_interested) if demande.Vehicul_interested else "Véhicule sélectionné",
            'montant_finance': demande.montant_souhaite,
            'duree': demande.duree_mois,
            'lien_offre': request.build_absolute_uri(f"/leads/offre/{demande.id}/"),
        }
        html_message = render_to_string('emails/documents/demande_accordee_client.html', context_email)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="✅ Félicitations ! Votre financement est accepté - KOZ Services",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[demande.client.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur envoi email au client: {e}")
    
    messages.success(request, "Dossier validé. Demande et vente enregistrées. Un email a été envoyé au client.")
    return redirect("leads_app:document-detail", dossier.pk)

@login_required
def modifier_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    
    # Vérifier que l'utilisateur est commercial ou directeur
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier ce dossier.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    if dossier.statut_dossier == "valide":
        messages.warning(request, "Ce dossier a déjà été validé, vous ne pouvez pas demander de modifications.")
    elif dossier.statut_dossier == "rejete":
        messages.warning(request, "Ce dossier a été rejeté. Une nouvelle demande de financement est nécessaire.")
    else:
        dossier.statut_dossier = "modification"
        dossier.save()
        messages.success(request, f"Une demande de modification a été envoyée à {dossier.client.nom_complet}.")
        
        # ✉️ Email au client
        try:
            context_email = {
                'client': dossier.client,
                'commercial': request.user,
                'dossier_id': dossier.id,
                'lien_chat': request.build_absolute_uri("/chat/"),
            }
            html_message = render_to_string('emails/documents/demande_modification_documents.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="📝 Demande de modification de vos documents - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[dossier.client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email au client: {e}")
        
        # 💬 Message dans le chat interne
        from chat_app.models import Message
        Message.objects.create(
            client=dossier.client,
            commercial=request.user,
            contenu=f"📄 Demande de modification de vos documents pour le dossier #{dossier.id}. Veuillez consulter votre espace client.",
            est_client=False,
        )
    
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
        # Récupérer le motif de rejet (depuis le formulaire)
        motif_rejet = request.POST.get('motif_rejet', 'Non conforme aux critères de financement')
        
        # 1️⃣ Rejeter le dossier
        dossier.statut_dossier = "rejete"
        dossier.commentaire_rejet = motif_rejet
        dossier.save()
        
        # 2️⃣ Mettre à jour l'étape de la demande
        demande.etape = "demand_refusee"
        demande.save()
        
        # 3️⃣ Si une vente existait, la passer en "perdue"
        vente = getattr(demande, 'vente', None)
        if vente:
            vente.statut = 'perdue'
            vente.save()
            messages.info(request, "La vente associée a été marquée comme perdue.")
        # ✉️ Email au client
        try:
            context_email = {
                'client': demande.client,
                'dossier_id': dossier.id,
                'demande_id': demande.id,
                'motif_rejet': motif_rejet,
                'commercial': request.user,
            }
            html_message = render_to_string('emails/document/dossier_rejete.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="❌ Votre dossier a été rejeté - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[demande.client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email au client: {e}")
        
        messages.success(request, "Dossier rejeté. Demande marquée comme refusée. Un email a été envoyé au client.")
    
    return redirect("leads_app:document-detail", dossier.pk)

@login_required
def verifier_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    
    if dossier.statut_dossier == "verification":
        messages.info(request, "Ce dossier est déjà en cours de vérification.")
    
    elif dossier.statut_dossier == "valide":
        messages.warning(request, "Ce dossier a été validé, vous ne pouvez pas le mettre en vérification.")
    
    elif dossier.statut_dossier == "rejete":
        messages.warning(request, "Ce dossier a été rejeté, vous ne pouvez pas le mettre en vérification.")
    
    else:
        dossier.statut_dossier = "verification"
        dossier.save()
        messages.success(request, "Ce dossier est désormais en cours de vérification.")
        
        # ✉️ Email au client
        try:
            context_email = {
                'client': dossier.client,
                'dossier_id': dossier.id,
                'demande_id': dossier.demande_financement.id,
                'lien_suivi': request.build_absolute_uri(f"/client/demandes/{dossier.demande_financement.id}/"),
            }
            html_message = render_to_string('emails/documents/dossier_verification.html', context_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject="🔄 Votre dossier est en cours de vérification - KOZ Services",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[dossier.client.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur envoi email au client: {e}")
    
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
    
        
    

    
    
        
    
    
