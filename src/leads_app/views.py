from datetime import timedelta, timezone, datetime
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import DemandeFinancementForm, GestionFinancementForm, DocumentsUploadForm
from commercial_app.forms import OffreFinancementForm
from .models import DevisLeads, Vente, demande_financement
from commercial_app.models import Offre
from vehicul_app.models import Vehicul
from client_app.models import Documents
from auth_app.models import kozUser


###API
from rest_framework import status #status = codes HTTP(200 = OK, 400 = Erreur, 500 = erreu server)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import DemandeFinancementSerializers

import logging

logger = logging.getLogger(__name__)

class ApiDemandeFinancementView(APIView):
    """ 
        API pour créer une demande de financement depuis le site web.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, vehicul_id):
        vehicule = get_object_or_404(Vehicul, id=vehicul_id)
        
        # ✅ 1. Vérifier que l'utilisateur est un client
        if request.user.role != "client":
            return Response(
                {"error": "Seuls les client faire une demande de financement."},
                status=status.HTTP_403_FORBIDDEN
            )
        # ✅ 2. Vérifier si une demande existe déjà
        demande_existante = demande_financement.objects.filter(
            client=request.user,
            etape__in=[
                "nouvelle", "en_attente", "en_cours","demande_accordee_fidelis",
                "demande_accordee_alios","demande_accordee_maison", 
                'demand_refusee'
            ]
        ).first()
        
        if demande_existante:
            return Response(
                 {"error": f"Une demande de financement est déjà {demande_existante.etape}."},
                 status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ 3. Validation des données
        serializer= DemandeFinancementSerializers(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # ✅ 4. Création de la demande
        try:
            demande = demande_financement.objects.create(
                client=request.user,
                Vehicul_interested=vehicule,
                apport=serializer.validated_data.get('apport', 0),
                duree_mois=serializer.validated_data.get('duree_mois', 36),
                revenus_mensuel=serializer.validated_data.get('revenus_mensuel', 0),
                etape="nouvelle",
                
            )
            # ✅ 5. Envoi de l'email au commercial assigné
            client = request.user
            if client.assigned_commercial and client.assigned_commercial.email:
                try:
                    context_email = {
                        'client': client,
                        'vehicule': f"{vehicule.marque.nom} {vehicule.modele} ({vehicule.annee})",
                        'apport': serializer.validated_data.get('apport', 0),
                        'duree': serializer.validated_data.get('duree_mois', 36),
                        'revenus': serializer.validated_data.get('revenus_mensuel', 0),
                        'lien_dashboard': request.build_absolute_uri(
                            reverse('commercial_app:commercial-view')
                        )
                    }
                    html_message = render_to_string(
                        'emails/demande_financement/demande_financement_envoyee.html',
                        context_email
                    )
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject="🆕 Nouvelle demande de financement - KOZ Services",
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.assigned_commercial.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Erreur envoi email au commercial: {e}")
            else:
                logger.warning(f"Client {client.email} n'a pas de commercial assigné")
            
            # ✅ 6. Réponse API (pas de messages !)
            return Response({
                 "message": "Demande de financement envoyée avec succès !",
                "demande_id": demande.id,
                "statut": demande.etape,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la demande: {str(e)}")
            return Response(
                {"error": "Une erreur est survenue lors de l'envoi de la demande."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
                
            


##################################################___Demande et Gestion de Financement_______###########################################
@login_required
def demande_financement_view(request, vehicul_id):
    
    vehicul = get_object_or_404(Vehicul, id=vehicul_id)
    
    if request.user.role != "client":
        messages.error(request, "Seuls les clients peuvent faire une demande.")
        return redirect("vehicul_app:detail-vehicul", vehicul_id=vehicul.pk)
    
    # Vérifier si une demande existe déjà
    demande_existante = demande_financement.objects.filter(
        client=request.user,
        etape__in=["nouvelle", "en_attente", "en_cours","demande_accordee_fidelis","demande_accordee_alios","demande_accordee_maison", 'demande_refusee']
    ).first()
    
    if demande_existante:
        messages.warning(request, f"Cette demande est déjà envoyée.")
        return redirect("client_app:client-view")
    
    if request.method == "POST":
        form = DemandeFinancementForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.client = request.user
            demande.Vehicul_interested = vehicul
            demande.etape = "nouvelle"
            demande.save()
            
            # ✉️ ENVOI DE L'EMAIL AU COMMERCIAL
            client = request.user  # ← Définir client ici
            
            # Vérifier que le client a bien un commercial assigné
            if client.assigned_commercial and client.assigned_commercial.email:
                try:
                    # Préparer le contexte (avant de l'utiliser)
                    context_email = {
                        'client': client,
                        'vehicule': f"{vehicul.marque.nom} {vehicul.modele} ({vehicul.annee})",
                        'apport': form.cleaned_data.get('apport', 0),
                        'duree': form.cleaned_data.get('duree_mois', 36),
                        'revenus': form.cleaned_data.get('revenus_mensuel', 0),
                        'lien_dashboard': request.build_absolute_uri(reverse('commercial_app:commercial-view'))
                    }
                    
                    html_message = render_to_string('emails/demande_financement/demande_financement_envoyee.html', context_email)
                    plain_message = strip_tags(html_message)
                    
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
                # Pas de notification, mais la demande est quand même créée
            
            return redirect("vehicul_app:detail-vehicul", vehicul.pk)
        
        else:
            # Formulaire invalide : rouvrir le modal
            context = {
                'vehicul': vehicul,
                'dmd_fin_form': form,
                'open_dmd_fin_modal': True,
            }
            return render(request, 'vehicul_templates/vehicul_detail.html', context)
    
    # Si GET (pas POST)
    return redirect("vehicul_app:detail-vehicul", vehicul.pk)

@login_required
def attente_document(request, demande_id):
    demande = get_object_or_404(demande_financement, id=demande_id)
    
    # === 1. VÉRIFICATION DU FINANCEMENT ===
    if not demande.financement_type:
        messages.error(request, "⚠️ Veuillez d'abord configurer le type de financement.")
        return redirect("leads_app:detail-demande", pk=demande.pk)
    
    if demande.financement_type == "externe" and not demande.financement_par:
        messages.error(request, "⚠️ Veuillez d'abord sélectionner le partenaire de financement (Fidelis/Alios).")
        return redirect("leads_app:detail-demande", pk=demande.pk)
    
    # === 2. VÉRIFICATION DE L'ETAPE ===
    if demande.etape == "en_attente":
        messages.info(request, "cette demande de financement est déjà en attente de document")
    elif demande.etape == "demande_accordee_fidelis" or demande.etape == "demande_accordee_alios" or demande.etape == "demande_accordee_maison":
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
                'lien_upload': request.build_absolute_uri(reverse("leads_app:detail-demande", args=[demande.pk])),
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
    elif demande.etape == "demande_accordee_fidelis" or demande.etape == "demande_accordee_alios" or demande.etape == "demande_accordee_maison":
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
                'lien_chat': request.build_absolute_uri(reverse("chat_app:chat-view")),
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
        
        
        
    
    return redirect("leads_app:detail-demande", demande.pk)    


@login_required
def estimer_prix_vehicule(request):
    # 1. On récupère les données GET (envoyées par HTMX)
    try:
        mensualite = Decimal(request.GET.get('mensualite_souhaitee', 0) or 0)
    except InvalidOperation:
        mensualite = Decimal(0)

    try:
        taux_annuel = Decimal(request.GET.get('taux_interet', 8) or 8) / Decimal(100)
    except InvalidOperation:
        taux_annuel = Decimal('0.08')

    try:
        duree_mois = int(request.GET.get('duree_mois', 36) or 36)
    except (TypeError, ValueError):
        duree_mois = 36

    try:
        apport = Decimal(request.GET.get('apport', 0) or 0)
    except InvalidOperation:
        apport = Decimal(0)

    if mensualite <= 0 or duree_mois <= 0:
        prix_vehicule = Decimal(0)
    else:
        taux_mensuel = taux_annuel / Decimal(12)

        if taux_mensuel == 0:
            capital = mensualite * duree_mois
        else:
            capital = mensualite * (1 - (1 + taux_mensuel) ** (-duree_mois)) / taux_mensuel

        prix_vehicule = capital + apport

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
            queryset = self.request.user.demande_financement.all().select_related("Vehicul_interested", "client").order_by("-date_creation")
            
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
            queryset = demande_financement.objects.all().order_by("-date_creation")
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
            context["offre_form"] = OffreFinancementForm(initial=initial)
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
                            'lien_demande': request.build_absolute_uri(reverse("leads_app:detail-demande", kwargs={"pk": demande.id}))
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
                
                return redirect('leads_app:detail-demande', demande.pk)
            else:
                # ❌ Dossier incomplet (documents manquants)
                dossier.statut_dossier = "incomplet"
                dossier.save()
                messages.warning(request, "Veuillez uploader tous les documents obligatoires.")
                
                # Réouvrir le modal avec le formulaire (conserve les fichiers déjà uploadés)
                context = {
                    'demande': demande,
                    'upload_doc_form': form,
                    'open_upload_doc_modal': True,
                }
                return render(request, 'clients_templates/client_demande_detail.html', context)
        else:
            # ❌ Formulaire invalide (erreur de validation)
            messages.error(request, "Erreur dans l'upload des fichiers. Vérifiez les champs.")
            
            # Réouvrir le modal avec le formulaire invalide
            context = {
                'demande': demande,
                'upload_doc_form': form,
                'open_upload_doc_modal': True,
            }
            return render(request, 'clients_templates/client_demande_detail.html', context)
    
    # Si GET (pas POST), rediriger vers la page de détail
    return redirect('leads_app:detail-demande', demande.pk)


@login_required
def upload_offre_documents(request, offre_id):
    """
    Vue pour uploader les documents d'une offre de financement.
    Le client upload ses documents, le dossier est vérifié.
    """
    # ✅ Récupérer l'offre (appartient au client connecté)
    offre = get_object_or_404(Offre, id=offre_id, client=request.user)
    
    # ✅ Récupérer ou créer le dossier de documents lié à l'offre
    dossier, created = Documents.objects.get_or_create(
        client=request.user,
        offre_financement=offre  # ← Ajoute ce champ dans ton modèle Documents
    )
    
    if request.method == "POST":
        form = DocumentsUploadForm(request.POST, request.FILES, instance=dossier)
        
        if form.is_valid():
            dossier = form.save()
            
            # ✅ Vérifier la complétude du dossier
            if dossier.verifier_completude():
                # ✅ Dossier complet → mise à jour des statuts
                dossier.statut_dossier = "complet"
                dossier.save()
                
                offre.statut = "verification_document"
                offre.save()
                
                messages.success(request, "✅ Dossier complet ! Il sera étudié prochainement.")
                
                # ✉️ Email à tous les commerciaux
                try:
                    commerciaux = kozUser.objects.filter(role="commercial")
                    for commercial in commerciaux:
                        if commercial and commercial.email:
                            context_email = {
                                'client': offre.client,
                                'offre_id': offre.id,
                                'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Non renseigné",
                                'lien_offre': request.build_absolute_uri(
                                    reverse('commercial_app:offre-detail', kwargs={'pk': offre.id})  # ← CORRIGÉ
                                )
                            }
                            html_message = render_to_string('emails/documents/dossier_offre_complet.html', context_email)
                            plain_message = strip_tags(html_message)
                            
                            send_mail(
                                subject="📄 Dossier complet à étudier - KOZ Services",
                                message=plain_message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[commercial.email],
                                html_message=html_message,
                                fail_silently=False,
                            )
                except Exception as e:
                    logger.error(f"Erreur envoi email aux commerciaux: {e}")
                
                return redirect('commercial_app:offre-detail', pk=offre.pk)
            
            else:
                # ❌ Dossier incomplet (documents manquants)
                dossier.statut_dossier = "incomplet"
                dossier.save()
                messages.warning(request, "⚠️ Veuillez uploader tous les documents obligatoires.")
                
                # ✅ Réouvrir le modal avec le formulaire
                context = {
                    'offre': offre,
                    'upload_doc_form': form,
                    'open_upload_doc_modal': True,
                }
                return render(request, 'clients_templates/offre_detail.html', context)  # ← CORRIGÉ
        
        else:
            # ❌ Formulaire invalide
            messages.error(request, "❌ Erreur dans l'upload des fichiers. Vérifiez les champs.")
            
            context = {
                'offre': offre,  # ← CORRIGÉ (demande → offre)
                'upload_doc_form': form,
                'open_upload_doc_modal': True,
            }
            return render(request, 'clients_templates/offre_detail.html', context)  # ← CORRIGÉ
    
    # ✅ GET → rediriger vers le détail de l'offre
    return redirect('commercial_app:offre-detail', pk=offre.pk)
                            
                            
    

@login_required
def valide_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    
    # === 1. VÉRIFICATIONS PRÉALABLES ===
    if dossier.statut_dossier == "incomplet":
        messages.error(request, "❌ Dossier incomplet : documents obligatoires manquants.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    if dossier.statut_dossier == "rejete":
        messages.warning(request, "⚠️ Dossier rejeté : ne peut pas être validé.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    if dossier.statut_dossier == "valide":
        messages.info(request, "ℹ️ Ce dossier est déjà validé.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    demande = dossier.demande_financement
    offre = dossier.offre_financement
    
    # ============================================================
    # CONTEXTE 1 : DEMANDE DE FINANCEMENT
    # ============================================================
    if demande:
        # Vérification du financement
        if not demande.financement_type:
            messages.error(request, "⚠️ Veuillez d'abord configurer le type de financement.")
            return redirect("leads_app:detail-demande", demande.pk)
        
        if demande.financement_type == "externe" and not demande.financement_par:
            messages.error(request, "⚠️ Veuillez d'abord sélectionner le partenaire de financement (Fidelis/Alios).")
            return redirect("leads_app:detail-demande", demande.pk)
        
        # Vérification : vente existante
        if hasattr(demande, 'vente') and demande.vente:
            messages.warning(request, "⚠️ Une vente est déjà enregistrée pour ce dossier.")
            return redirect("leads_app:document-detail", dossier.pk)
        
        # ✅ Déterminer le partenaire et le statut
        if demande.financement_type == "externe":
            if demande.financement_par == "fidelis":
                nouvelle_etape = "demande_accordee_fidelis"
                partenaire = "Fidelis"
            elif demande.financement_par == "alios":
                nouvelle_etape = "demande_accordee_alios"
                partenaire = "Alios"
            else:
                messages.error(request, "⚠️ Partenaire de financement externe non reconnu.")
                return redirect("leads_app:document-detail", dossier.pk)
        else:
            nouvelle_etape = "demande_accordee_maison"
            partenaire = "KOZ Services (financement interne)"
        
        # ✅ CRÉER LA VENTE AVANT DE CHANGER LE STATUT
        Vente.objects.create(
            client=demande.client,
            demande_financement=demande,
            statut='conclue',
            montant=demande.Vehicul_interested.prix if demande.Vehicul_interested else 0
        )
        
        # ✅ Mettre à jour la demande
        demande.etape = nouvelle_etape
        demande.save()
        
        client = demande.client
        context_email = {
            'client': client,
            'demande_id': demande.id,
            'partenaire': partenaire,
            'vehicule': str(demande.Vehicul_interested) if demande.Vehicul_interested else "Véhicule sélectionné",
            'montant_finance': demande.Vehicul_interested.prix if demande.Vehicul_interested else 0,
            'duree': demande.duree_mois,
            'lien_dossier': request.build_absolute_uri(
                reverse("leads_app:document-detail", kwargs={"pk": dossier.pk})
            ),
        }
    
    # ============================================================
    # CONTEXTE 2 : OFFRE DE FINANCEMENT
    # ============================================================
    elif offre:
        # Vérification du financement
        if not offre.financement_type:
            messages.error(request, "⚠️ Veuillez d'abord configurer le type de financement de l'offre.")
            return redirect("commercial_app:offre-detail", offre.pk)
        
        if offre.financement_type == "externe" and not offre.financement_par:
            messages.error(request, "⚠️ Veuillez d'abord sélectionner le partenaire de financement (Fidelis/Alios).")
            return redirect("commercial_app:offre-detail", offre.pk)
        
        # Vérification : vente existante
        if hasattr(offre, 'vente') and offre.vente:
            messages.warning(request, "⚠️ Une vente est déjà enregistrée pour cette offre.")
            return redirect("leads_app:document-detail", dossier.pk)
        
        # ✅ Déterminer le partenaire et le statut
        if offre.financement_type == "externe":
            if offre.financement_par == "fidelis":
                nouveau_statut = "offre_financement_fidelis"
                partenaire = "Fidelis"
            elif offre.financement_par == "alios":
                nouveau_statut = "offre_financement_alios"
                partenaire = "Alios"
            else:
                messages.error(request, "⚠️ Partenaire de financement externe non reconnu.")
                return redirect("leads_app:document-detail", dossier.pk)
        else:
            nouveau_statut = "offre_financement_maison"
            partenaire = "KOZ Services (financement interne)"
        
        # ✅ CRÉER LA VENTE AVANT DE CHANGER LE STATUT
        Vente.objects.create(
            client=offre.client,
            offre_financement=offre,
            statut='conclue_par_acceptation_offre_financement',
            montant=offre.vehicule_propose.prix if offre.vehicule_propose else 0
        )
        
        # ✅ Mettre à jour l'offre
        offre.statut = nouveau_statut
        offre.save()
        
        client = offre.client
        context_email = {
            'client': client,
            'offre_id': offre.id,
            'partenaire': partenaire,
            'vehicule': str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné",
            'montant_finance': offre.vehicule_propose.prix if offre.vehicule_propose else 0,
            'duree': offre.duree_mois,
            'lien_dossier': request.build_absolute_uri(
                reverse("leads_app:document-detail", kwargs={"pk": dossier.pk})
            ),
        }
    
    else:
        messages.error(request, "❌ Aucune demande ni offre associée à ce dossier.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # ============================================================
    # ✅ VALIDATION DU DOSSIER (APRÈS TOUTES LES CRÉATIONS)
    # ============================================================
    dossier.statut_dossier = "valide"
    dossier.save()
    
    # ============================================================
    # ENVOI DE L'EMAIL
    # ============================================================
    try:
        html_message = render_to_string('emails/documents/dossier_valide.html', context_email)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="✅ Félicitations ! Votre financement est accepté - KOZ Services",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur envoi email au client: {e}")
    
    messages.success(request, "✅ Dossier validé. Demande et vente enregistrées. Un email a été envoyé au client.")
    return redirect("leads_app:document-detail", pk=dossier.pk)

@login_required
def modifier_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    
    # Vérifier que l'utilisateur est commercial ou directeur
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "❌ Vous n'avez pas l'autorisation de modifier ce dossier.")
        return redirect("leads_app:document-detail", pk=dossier.pk)
    
    # Vérifier si le dossier peut être modifié
    if dossier.statut_dossier == "valide":
        messages.warning(request, "⚠️ Ce dossier a déjà été validé, vous ne pouvez pas demander de modifications.")
        return redirect("leads_app:document-detail", pk=dossier.pk)
    
    if dossier.statut_dossier == "rejete":
        messages.warning(request, "⚠️ Ce dossier a été rejeté. Une nouvelle demande de financement est nécessaire.")
        return redirect("leads_app:document-detail", pk=dossier.pk)
    
    # ✅ Mise à jour du statut
    dossier.statut_dossier = "modification"
    dossier.save()
    
    # ✅ Déterminer le contexte (demande ou offre)
    demande = dossier.demande_financement
    offre = dossier.offre_financement
    
    if demande:
        contexte_nom = "demande de financement"
        vehicule = str(demande.Vehicul_interested) if demande.Vehicul_interested else "Véhicule sélectionné"
        lien_demande_offre = request.build_absolute_uri(
            reverse("leads_app:detail-demande", kwargs={"pk": demande.id})
        )
    elif offre:
        contexte_nom = "offre de financement"
        vehicule = str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné"
        lien_demande_offre = request.build_absolute_uri(
            reverse("commercial_app:offre-detail", kwargs={"pk": offre.id})
        )
    else:
        contexte_nom = "dossier"
        vehicule = "Non renseigné"
        lien_demande_offre = None
    
    messages.success(
        request, 
        f"✅ Une demande de modification a été envoyée à {dossier.client.nom_complet} pour son {contexte_nom}."
    )
    
    # ✉️ EMAIL AU CLIENT
    try:
        context_email = {
            'client': dossier.client,
            'commercial': request.user,
            'dossier_id': dossier.id,
            'contexte': contexte_nom,
            'vehicule': vehicule,
            'lien_chat': request.build_absolute_uri(reverse("chat_app:chat-view")),
            'lien_dossier': request.build_absolute_uri(
                reverse("leads_app:document-detail", kwargs={"pk": dossier.pk})
            ),
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
    
    # 💬 MESSAGE DANS LE CHAT INTERNE
    try:
        from chat_app.models import Message
        
        if demande:
            message_contenu = (
                f"📄 Demande de modification de vos documents pour la demande de financement "
                f"du véhicule {vehicule}. Veuillez consulter votre espace client."
            )
        elif offre:
            message_contenu = (
                f"📄 Demande de modification de vos documents pour l'offre de financement "
                f"n°{offre.id} (véhicule {vehicule}). Veuillez consulter votre espace client."
            )
        else:
            message_contenu = (
                f"📄 Demande de modification de vos documents pour votre dossier. "
                f"Veuillez consulter votre espace client."
            )
        
        Message.objects.create(
            client=dossier.client,
            commercial=request.user,
            contenu=message_contenu,
            est_client=False,
        )
    except Exception as e:
        print(f"Erreur création message chat: {e}")
    
    return redirect("leads_app:document-detail", dossier.pk)

@login_required
def rejete_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    
    # Vérifier que l'utilisateur est commercial ou directeur
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "❌ Vous n'avez pas l'autorisation de rejeter ce dossier.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # Vérifier si le dossier peut être rejeté
    if dossier.statut_dossier == "rejete":
        messages.info(request, "ℹ️ Ce dossier est déjà rejeté.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    if dossier.statut_dossier == "valide":
        messages.warning(request, "⚠️ Ce dossier a été validé, vous ne pouvez pas le rejeter.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # Récupérer le motif de rejet (depuis le formulaire)
    motif_rejet = request.POST.get('motif_rejet', 'Non conforme aux critères de financement')
    
    # ✅ Déterminer le contexte (demande ou offre)
    demande = dossier.demande_financement
    offre = dossier.offre_financement
    
    # ============================================================
    # CONTEXTE 1 : DEMANDE DE FINANCEMENT
    # ============================================================
    if demande:
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
            vente.statut = 'perdue_par_rejet_dossier_demande_financement'
            vente.save()
            messages.info(request, "La vente associée a été marquée comme perdue.")
        
        
        # 5️⃣ Contexte pour l'email
        contexte_nom = "demande de financement"
        contexte_id = demande.id
        contexte_type = "demande"
        client = demande.client
        
        # 6️⃣ Message de succès
        messages.success(request, "✅ Dossier rejeté. Demande marquée comme refusée. Un email a été envoyé au client.")
    
    # ============================================================
    # CONTEXTE 2 : OFFRE DE FINANCEMENT
    # ============================================================
    elif offre:
        # 1️⃣ Rejeter le dossier
        dossier.statut_dossier = "rejete"
        dossier.commentaire_rejet = motif_rejet
        dossier.save()
        
        # 2️⃣ Mettre à jour le statut de l'offre
        offre.statut = 'offre_document_rejete'
        offre.save()
        
        # 3️⃣ Si une vente existait, la passer en "perdue"
        vente = getattr(offre, 'vente', None)
        if vente:
            vente.statut = 'perdue_par_rejet_dossier_offre_financement'
            vente.save()
            messages.info(request, "La vente associée a été marquée comme perdue.")
        
        # 4️⃣ Contexte pour l'email
        contexte_nom = "offre de financement"
        contexte_id = offre.id
        contexte_type = "offre"
        client = offre.client
        
        # 5️⃣ Message de succès
        messages.success(request, "✅ Dossier rejeté. Offre marquée comme refusée. Un email a été envoyé au client.")
    
    else:
        messages.error(request, "❌ Aucune demande ni offre associée à ce dossier.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # ============================================================
    # ENVOI DE L'EMAIL
    # ============================================================
    try:
        context_email = {
            'client': client,
            'dossier_id': dossier.id,
            'contexte_nom': contexte_nom,
            'contexte_id': contexte_id,
            'contexte_type': contexte_type,
            'motif_rejet': motif_rejet,
            'commercial': request.user,
            'lien_chat': request.build_absolute_uri(reverse("chat_app:chat-view")),
        }
        html_message = render_to_string('emails/documents/dossier_rejete.html', context_email)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="❌ Votre dossier a été rejeté - KOZ Services",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur envoi email au client: {e}")
    
    # 💬 MESSAGE DANS LE CHAT INTERNE
    try:
        from chat_app.models import Message
        Message.objects.create(
            client=client,
            commercial=request.user,
            contenu=f"❌ Votre {contexte_nom} (n°{contexte_id}) a été rejetée. Motif : {motif_rejet}. N'hésitez pas à discuter avec nous via le chat.",
            est_client=False,
        )
    except Exception as e:
        print(f"Erreur création message chat: {e}")
    
    return redirect("leads_app:document-detail", pk=dossier.pk)

@login_required
def verifier_dossier(request, dossier_id):
    dossier = get_object_or_404(Documents, id=dossier_id)
    
    # Vérifier que l'utilisateur est commercial ou directeur
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "❌ Vous n'avez pas l'autorisation de mettre ce dossier en vérification.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # Vérifier si le dossier peut être mis en vérification
    if dossier.statut_dossier == "verification":
        messages.info(request, "ℹ️ Ce dossier est déjà en cours de vérification.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    if dossier.statut_dossier == "valide":
        messages.warning(request, "⚠️ Ce dossier a été validé, vous ne pouvez pas le mettre en vérification.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    if dossier.statut_dossier == "rejete":
        messages.warning(request, "⚠️ Ce dossier a été rejeté, vous ne pouvez pas le mettre en vérification.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # ✅ Mise à jour du statut
    dossier.statut_dossier = "verification"
    dossier.save()
    messages.success(request, "✅ Ce dossier est désormais en cours de vérification.")
    
    # ✅ Déterminer le contexte (demande ou offre)
    demande = dossier.demande_financement
    offre = dossier.offre_financement
    
    if demande:
        contexte_nom = "demande de financement"
        contexte_id = demande.id
        vehicule = str(demande.Vehicul_interested) if demande.Vehicul_interested else "Véhicule sélectionné"
    elif offre:
        contexte_nom = "offre de financement"
        contexte_id = offre.id
        vehicule = str(offre.vehicule_propose) if offre.vehicule_propose else "Véhicule sélectionné"
    else:
        contexte_nom = "dossier"
        contexte_id = None
        vehicule = "Non renseigné"
    
    # ✉️ EMAIL AU CLIENT
    try:
        context_email = {
            'client': dossier.client,
            'dossier_id': dossier.id,
            'contexte_nom': contexte_nom,
            'contexte_id': contexte_id,
            'vehicule': vehicule,
            'lien_suivi': request.build_absolute_uri(
                reverse('leads_app:document-detail', kwargs={"pk": dossier.pk})
            ),
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
    
    return redirect("leads_app:document-detail", pk=dossier.pk)
       
@login_required
def reverifier_document(request, dossier_id):
    """
    Remet un dossier en vérification (après correction par le client)
    Utilisable pour les dossiers liés à une demande OU à une offre
    """
    dossier = get_object_or_404(Documents, id=dossier_id)
    
    # Vérifier que l'utilisateur est commercial ou directeur
    if request.user.role not in ['commercial', 'directeur']:
        messages.error(request, "❌ Action non autorisée.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # Vérifier que le dossier a un contexte (demande ou offre)
    demande = dossier.demande_financement
    offre = dossier.offre_financement
    
    if not demande and not offre:
        messages.error(request, "❌ Cette action n'est disponible que pour les dossiers liés à une demande ou une offre de financement.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # Vérifier que le dossier est dans un état valide pour être revérifié
    if dossier.statut_dossier not in ['rejete', 'modification']:
        messages.warning(request, "⚠️ Ce dossier ne peut pas être remis en vérification.")
        return redirect("leads_app:document-detail", dossier.pk)
    
    # ✅ Remettre en vérification
    dossier.statut_dossier = "verification"
    dossier.commentaire_rejet = ""  # Effacer le commentaire de rejet
    dossier.save()
    
    # ✅ Mettre à jour le contexte selon le type
    if demande:
        contexte_nom = "demande de financement"
        contexte_id = demande.id
        if demande.etape in ['demand_refusee']:
            demande.etape = "en_cours"
            demande.save()
    elif offre:
        contexte_nom = "offre de financement"
        contexte_id = offre.id
        if offre.statut in ['refusee', 'expiree',"offre_document_rejete"]:
            offre.statut = "envoyee"
            offre.save()
    else:
        contexte_nom = "dossier"
        contexte_id = None
    
    # ✅ Déterminer le message de succès
    if demande:
        messages.success(request, f"✅ Le dossier de {dossier.client.nom_complet} est à nouveau en vérification pour sa demande n°{demande.id}.")
    elif offre:
        messages.success(request, f"✅ Le dossier de {dossier.client.nom_complet} est à nouveau en vérification pour son offre n°{offre.id}.")
    else:
        messages.success(request, f"✅ Le dossier de {dossier.client.nom_complet} est à nouveau en vérification.")
    
    # ✉️ EMAIL AU CLIENT
    try:
        context_email = {
            'client': dossier.client,
            'dossier_id': dossier.id,
            'contexte_nom': contexte_nom,
            'contexte_id': contexte_id,
            'lien_dossier': request.build_absolute_uri(
                reverse("leads_app:document-detail", kwargs={"pk": dossier.pk})
            ),
        }
        html_message = render_to_string('emails/documents/dossier_reverification.html', context_email)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="🔄 Votre dossier est à nouveau en vérification - KOZ Services",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[dossier.client.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur envoi email au client: {e}")
    
    # 💬 MESSAGE DANS LE CHAT INTERNE
    try:
        from chat_app.models import Message
        Message.objects.create(
            client=dossier.client,
            commercial=request.user,
            contenu=f"🔄 Votre {contexte_nom} (n°{contexte_id}) a été remise en vérification. Merci de votre diligence.",
            est_client=False,
        )
    except Exception as e:
        print(f"Erreur création message chat: {e}")
    
    return redirect("leads_app:document-detail", dossier.pk)

class DocumentListView(LoginRequiredMixin, ListView):
    model = Documents
    context_object_name = "documents"
    
    def get_template_names(self):
        is_htmx = self.request.headers.get("HX-Request") == "true"  # ← Correction : HX-Request (majuscule)
        
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return ["partials/documents/dir_list_doc.html" if is_htmx else "directeur_templates/directeur_list_doc.html"]
        
        if self.request.user.is_staff or self.request.user.role == "commercial":
            return ["partials/documents/com_list_doc.html" if is_htmx else "commercial_templates/commercial_list_doc.html"]
        
        return ["partials/documents/cli_list_doc.html" if is_htmx else "clients_templates/client_list_doc.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statut_choices"] = Documents.STATUT_DOCS
        return context
    
    def get_base_queryset(self):
        """Détermine le queryset de base selon le rôle de l'utilisateur"""
        user = self.request.user
        
        if user.is_superuser or user.role == "directeur":
            return Documents.objects.all().order_by("-date_upload")
        
        if user.is_staff or user.role == "commercial":
            return Documents.objects.all().order_by("-date_upload")
        
        if user.role == "client":
            return Documents.objects.filter(client=user).order_by("-date_upload")
        
        return Documents.objects.none()
    
    def apply_filters(self, queryset):
        """Applique les filtres communs (GET parameters)"""
        q = self.request.GET.get("q")
        statut = self.request.GET.get("statut")
        client_name = self.request.GET.get("client_name")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        
        if q:
            queryset = queryset.filter(
                Q(statut_dossier__icontains=q) |
                Q(client__nom_complet__icontains=q) |
                Q(demande_financement__Vehicul_interested__marque__nom__icontains=q) |
                Q(demande_financement__Vehicul_interested__modele__icontains=q) |
                Q(commentaire_rejet__icontains=q) |  # ← Correction : commentaire_rejet (pas commentaires)
                Q(demande_financement__etape__icontains=q) |
                Q(demande_financement__financement_type__icontains=q) |
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
    
    def get_queryset(self):
        # Base queryset selon le rôle
        queryset = self.get_base_queryset().order_by("-date_upload")
        
        # Optimisation avec select_related
        queryset = queryset.select_related("client", "demande_financement").order_by("-date_upload")
        
        # Application des filtres
        queryset = self.apply_filters(queryset).order_by("-date_upload")
        
        return queryset
            
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
        dossier = self.object
        
        if dossier.verifier_completude():
            dossier.statut_dossier = "complet"
            dossier.save()
            if dossier.demande_financement:
                dossier.demande_financement.etape = "en_cours"
                dossier.demande_financement.save()
        
        messages.success(self.request, "Vos documents ont été mis à jour")
        return response
    
    def form_invalid(self, form):
        doc_detail_view = DocumentDetailView()
        doc_detail_view.request = self.request
        doc_detail_view.kwargs = self.kwargs
        context = doc_detail_view.get_context_data()
        context["open_update_doc_modal"] = True
        context["update_doc_form"] = form
        return self.render_to_response(context)
    
class DocumentDeleteView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    def test_func(self):
        doc = self.get_object()
        return doc.statut_dossier == "rejete"
    model = Documents
    template_name = "clients_templates/client_detail.doc.html"
    success_url = reverse_lazy("leads_app:documents-list")
    
        
    

    
    
        
    
    