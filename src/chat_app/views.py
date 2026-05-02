from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from django.http import HttpResponse

from auth_app.models import kozUser
from .models import Message

@login_required
def envoyer_message(request, client_id=None):
   if request.method == "POST":   
      contenu = request.POST.get("contenu")  
      if not contenu or not contenu.strip():
         return HttpResponse('')
      
      if request.user.role == "client":
         client = request.user
         commercial = client.assigned_commercial
         
         message = Message.objects.create(
            client=client,
            commercial=commercial,
            contenu=contenu.strip(),
            est_client=True
         )
         
      else:
         commercial = request.user
         client = get_object_or_404(kozUser, id=client_id, role="client")
         message = Message.objects.create(
            client=client,
            commercial=commercial,
            contenu=contenu,
            est_client=False
         )
    
   return render(request, "partials/chat/message.html", {'message': message,
                                                               'client': client,})


@login_required
def chat_view(request, client_id=None):
   if request.user.role == "client":
      messages = Message.objects.filter(client=request.user).order_by('-date_envoi')
      destinataire = request.user.assigned_commercial
      context = {
            'messages': messages,
            'destinataire': destinataire,
            'client_id': request.user.id,
      }
   
   else:
      client = get_object_or_404(kozUser, id=client_id, role="client")
      messages = Message.objects.filter(client=client).order_by('date_envoi')
      context = {
            'messages': messages,
            'client': client,
            'client_id': client.id,
        }
   return render( request, "chat_templates/chat.html", context)