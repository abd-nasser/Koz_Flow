from django.shortcuts import render
from django.contrib.auth import(
                                authenticate, 
                                login as django_login, 
                                logout as django_logout) 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import(
    TemplateView, ListView, CreateView, FormView,
    UpdateView, DeleteView, DetailView
)

from django.contrib.auth.mixins import(
    LoginRequiredMixin, UserPassesTestMixin
)

from rest_framework import status #status = codes HTTP(200 = OK, 400 = Erreur, 500 = erreu server)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken



from .serializers import RegisterSerializers, UserSerializer
from .forms import UserRegisterForm, ChangePasswordForm
from .models import kozUser

import logging

logger = logging.getLogger(__name__)

#------------- VUE POUR L'INSCRIPTION ----------------------
#APIView = une vue qui répond aux requetes GET, POST, PUT, DELETE
#@method_decorator(csrf_exempt, name='dispatch')
class ApiRegisterView(APIView):
    #Tout le monde peut s'inscrie
    permission_classes = [AllowAny]
    
    def post(self, request):
            #on recupère les donné envoyé par user
        try:
            serializer = RegisterSerializers(data=request.data)
            
            #si les données sont valide on creer user
            if serializer.is_valid:
                user = serializer.save()
                    
                # on actualise les tokens du user
                refresh = RefreshToken.for_user(user)
                    
                #Si tout est ok en renvoie une reponse en json
                return Response({
                        'utilisateur': RegisterSerializers(user).data, # on renvoie les données du user créé
                        'token': str(refresh), # on renvoie le token de rafraichissement
                        'acces': str(refresh.access_token), # on renvoie le token d'accès
                    }, status=status.HTTP_201_CREATED) # 201 = Créé avec succès
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) #
                
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {str(e)}")
            return Response(
                    {"error":"Une erreur est survenue lors de l'inscription"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                                )
        
# ----- VUE POUR LA CONNEXION -----
#@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes= [AllowAny] # Tout le monde peut se connecter
    
    def post(self, request):
        #recupère l'email et le password
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            print(f"Email: {email}, Password: {password}")  # Debug: Affiche les données reçues
            
            user = authenticate(request, email=email, password=password) 

            print(f"User: {user}")  # Debug: Affiche l'utilisateur trouvé

            if user is not None:
                
                django_login(request, user)
                refresh = RefreshToken.for_user(user)
                
                if user.is_superuser or user.role == "directeur":
                    redirect_url = 'directeur/dashboard/'
                    
                elif user.role == 'commercial':
                    redirect_url = 'commercial/dashboard/'
                
                else:
                    redirect_url = 'client/dashboard/'    
                
                # on renvoie la reponse avec les tokens et la redirection
                
                return Response({
                    'access':str(refresh.access_token),
                    'refresh':str(refresh),
                    'user':UserSerializer(user).data,
                    'redirect_url': redirect_url,
                }, status=status.HTTP_200_OK) # 200 = OK
            else:
                # Si l'authentification a échoué (mauvais email ou mot de passe)
                return Response({"error":"Email ou mot de passe incorrect"},
                                status=status.HTTP_401_UNAUTHORIZED # 401 = Non autorisé
                                )
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {str(e)}")
            return Response({"error":"Une erreur est survenue lors de la connexion"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )


# ----- VUE POUR OBTENIR L'UTILISATEUR CONNECTÉ -----
class MeView(APIView):
    # IsAuthenticated = SEUL les utilisateurs connectés peuvent voir cette page
    # Si tu n'es pas connecté, Django renvoie une erreur 401 automatiquement
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
         # request.user = l'utilisateur qui a fait la requête (grâce au token JWT)
         # On le sérialise en JSON et on le renvoie
            return Response(UserSerializer(request.user).data)

# ----- VUE POUR LA DÉCONNEXION -----
class LogoutView(APIView):
    permission_classes = [IsAuthenticated] #Uniquement user connecté
    
    def post(self, request):
        try:
            #on récupère le refresh token stock par le client lors de sa connection
            refresh_token = request.data.get('refresh')
            
            #on creé une instance RefreshToken à partir du token recupére
            token = RefreshToken(refresh_token)
            
            #on blacklist le token recupérer
            token.blacklist()     
            return Response({"message":"déconnection reussi"})
            
        except Exception as e:
            logger.error(f"erreur coté serveur = {str(e)} ")
            return Response({"erreur":f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    
    


#--------------------------LES Vus d'autentification pour ERP--------------------------
#---------------------------------------------------------------------------------------

class UserRegisterView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = kozUser
    form_class = UserRegisterForm
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return ["directeur_templates/directeur.html"]    
        else:
            return ["commercial_templates/commercial.html"]
   
    def get_success_url(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return reverse_lazy("directeur_app:directeur-view")
        elif self.request.user.role == "commercial":
            return reverse_lazy("commercial_app:commercial-view")
        else:
            return reverse_lazy("client_app:client-view")
       
    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs["created_by"] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Ne jamais afficher le mot de passe dans l'interface
        # Juste un message générique
        messages.success(self.request, 
            f"✅ Utilisateur {form.cleaned_data.get('email')} créé !\n"
            f"📧 Les identifiants temporaires ont été envoyés par email."
        )
        
        return response
    
    def form_invalid(self, form):
        #Quand le formulaire est invalide, on reste sur la meme page
        #on passe le formulaire invalide au context
        context = self.get_context_data()
        context["user_register_form"] = form
        context["reopen_modal"] = True # variable pour réouvrir le modal avec les erreurs
        return self.render_to_response(context)
      
      
      
class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm
    
    def get_template_names(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return ["directeur_templates/directeur.html"]
        elif self.request.user.role == "commercial":
            return ["commercial_templates/commercial.html"]
        else:
            return ["client_templates/client.html"]
           
    def get_success_url(self):
        if self.request.user.is_superuser or self.request.user.role == "directeur":
            return reverse_lazy("directeur_app:directeur-view")
        elif self.request.user.role == "commercial":
            return reverse_lazy("commercial_app:commercial-view")
        else:
            return reverse_lazy("client_app:client-view")

    def get_form_kwargs(self):
        kwargs =  super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Récupère le nouveau mot de passe
        new_password = form.cleaned_data.get("new_password")
        
        # Change le mot de passe
        user = self.request.user
        user.set_password(new_password)
        user.save()
        
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(self.request, user)
        
        # Message de succès
        messages.success(self.request, "Votre mot de passe a été changé avec succès !")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        #Quand le formulaire est invalide, on reste sur la meme page
        # on passe le formulaire invalide au context
        context = self.get_context_data()
        context["change_pass_form"] = form
        context["reopen_modal"] = True # variable pour réouvrir le modal avec les erreurs
        return self.render_to_response(context)
        
    
    
        
        
         
    
    