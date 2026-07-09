import django
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse


#REST_FRAMEWORK
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

#MODELS
from .models import Paiement
from order_app.models import Commande

#PACKAGE
import json
import hashlib
import hmac
import requests
import logging

logger = logging.getLogger(__name__)

class ApiPaiementView(APIView):
    """ 
    API pour initier un paiement via LigdiCASH (Orange Money BF),
    POST /api/paiements/Initier
    
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1️⃣ Récuperer les données du clients
        commande_id = request.data.get("commande_id")
        telephone = request.data.get("telephone")
        otp = request.data.get('otp')
        montant = request.data.get('montant')
        
        
        # 2️⃣ Vérification de base
        if not all([commande_id, telephone, otp, montant]):
            return Response({"error":"commande_id, telephone, otp, montant sont requis"},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # 3️⃣ Vérifier que la commande existe et appartient au client
        commande  = get_object_or_404(Commande,
                                      id=commande_id,
                                      panier__client=request.user
                                      )
        
        
        # 4️⃣ Vérifier que le montant correspond
        if int(montant) != commande.panier.total_panier():
            return Response({"error":"Le montant ne correspond pas au total du panier"}, 
                            status=status.HTTP_400_BAD_REQUEST)
            
        
        # 5️⃣Construire le payload Ligdicash
        payload = {
            "commande":{
                "invoice":{
                    "total_amount": int(montant),
                    "devise": "XOF",
                    "description":f"Commande KOZ SERVICES #{commande.id}",
                    "customer":telephone,
                    "customer_firstname":request.user.nom_complet.split[0] if request.user.nom_complet else "Client",
                    "customer_lasttname":request.user.nom_complet.split[1] if request.user.nom_complet else "KOZ",
                    "customer_email":request.user.email,
                    "otp":otp
                },
                "store":{
                    "name":"KOZ Services",
                    "website_url":"https//www.koz-corporate.pro"
                },
                "actions":{
                    "callback_url": request.build.absolute_uri(
                        reverse("paiement_app:callback-ligdicash")
                        )
                },
                "custom_data":{
                    "commande_id":commande.id,
                    "client_id": request.user.id,
                }
            }
        }
        
        # 6️⃣ Envoyer la requet à Ligdicash
        try:
            response = requests.post(
                "https://app.ligdicash.com/pay/v01/straight/checkout-invoice/create",
                headers={
                    "Apikey":settings.LIGDICASH_API_KEY,
                    "Authorization":f'Bearer {settings.LIGDICASH_API_TOKEN}',
                    "Accept":"application/json",
                    "Content-Type":"application/json"
                },
                json=payload,
                timeout=30
                )
            data = response.json()
            if response.status_code == 200 and data.get('response_code') == '00':
                # 7️⃣ Créer le transaction en base
                paiement = Paiement.objects.create(
                    commande=commande,
                    client = request.user,
                    token = data.get('token'),
                    statut= "en_attente"
                )
                
                return Response({
                    "message":"Paiement initié avec succès",
                    "token": data.get("token"),
                    "paiement_id": paiement.id,
                    "status": paiement.statut,
                    "response_text": data.get("response_text"), 
                }, status=status.HTTP_200_OK)
            else:
                # Erreur Ligdicash
                return Response({
                    "error":data.get('response_text', "Erreur inconnue"),
                    "code": data.get("response_code"),
                    
                }, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.Timeout:
            return Response({
                "error":"le paiement à expiré. Veuillez réessayer"
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        except Exception as e:
            return Response({
                "error":f"Erreur serveur: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                

@csrf_exempt # Token csrf impossible
@require_POST
def callback_ligdicash(request):
    """
    Webhook reçu de ligdicash pour confirmer le paiement,
    Ligdicash envoie une requete Post à cette URL 
    
    """
    try:
        #1️⃣ Récuperer le payload JSON
        payload = json.loads(request.body)
        logger.info(f"Callback reçu de ligdiCash: {payload}")
        
        #2️⃣ Extraire les données essentielles
        token = payload.get("token"),
        status = payload.get("status"),
        transaction_id = payload.get('transaction_id')
        montant = payload.get("amount")
        
        #3️⃣ Vérifier que le token existe
        if not token :
            logger.error("Callback sans token")
            return JsonResponse({"error":"Token manquant"}, status=400)
        
        #4️⃣ Récupere le paiement correspondant
        paiement = get_object_or_404(Paiement, token=token)
        
        #5️⃣ Verification de sécurité : le montant doit correspondre
        if montant and int(montant) != paiement.montant:
            logger.error(f"Montant incoherent: reçu {montant}, attendu {paiement.montant}")
            return JsonResponse({"error":"Montant incohérent"}, status=400)
        
        #6️⃣ Verification de sécurité: la commande est bien liée
        commande = paiement.commande
        if not commande:
            return JsonResponse({"error":"commande introuvable"}, status=400)
        
        #7️⃣ Mettre à jour le statut du paiement
        if status == 'success':
            paiement.statut = "reussi"
            paiement.ligdicash_transaction_id = transaction_id
            paiement.methode = "mobile_ligdicash"
            paiement.save()
            
            # ✅ Mettre à jour la commande
            commande.statut = "payee"
            commande.save()
            logger.info(f'✅ Paiement {paiement.id} confirmé pour la commande {commande.id}')

            send_mail(
                subject="Paiement confirmé",
                message=f"Votre paiement pour la commande {commande.id} a été confirmé.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[commande.panier.client.email],
            )
            
            return JsonResponse({
                "message":"Paiement confirmé",
                "paiement_id": paiement.id,
                "commande_id": commande.id,
                "status": paiement.statut
            })
            
        elif status == 'failed':
            paiement.statut = "echec" 
            paiement.save()
            logger.warning(f'❌ Paiement {paiement.id} échoué pour la commande {commande.id}')
            return JsonResponse({
                "message":"Paiement échoué",
                "paiement_id": paiement.id,
                "commande_id": commande.id,
                "status": paiement.statut
            })
        else:
            logger.warning(f'⚠️ Callback reçu avec un statut inconnu: {status}')
            return JsonResponse({
                "message":"Statut inconnu",
                "paiement_id": paiement.id,
                "commande_id": commande.id,
                "status": paiement.statut
            })
    except json.JSONDecodeError:
        logger.error("Payload JSON invalide")
        return JsonResponse({"error":"Payload JSON invalide"}, status=400)  
            
            
    except Exception as e:
        logger.exception(f"Erreur lors du traitement du callback: {str(e)}")
        return JsonResponse({"error":f"Erreur serveur: {str(e)}"}, status=500)
    
    
    
def verifier_signature(request, payload):
    """
    Vérifie que le callback vient bien de LigdiCash.
    La signature est généralement dans un header X-Signature.
    """
    signature = request.headers.get('X-Signature')
    if not signature:
        logger.warning("Aucune signature dans le callback")
        return False

    # Générer la signature avec la clé secrète
    secret = settings.LIGDICASH_SECRET_KEY
    computed = hmac.new(
        secret.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, signature)