from django.db import models
from auth_app.models import kozUser

class Message(models.Model):
    #Qui envoie ? (None = c'est le commercial qui a envoyé)
    #on va gerer l'expéditeur dans la vue, pas besoin de champ ici 
    client = models.ForeignKey(
        kozUser, 
        on_delete=models.CASCADE, 
        related_name="messages_envoyes", 
        limit_choices_to={'role': 'client'}
        )
     
    commercial =  models.ForeignKey(
        kozUser, 
        on_delete=models.SET_NULL,
        null=True, 
        related_name="messages_recus", 
        limit_choices_to={"role":'commercial'}
        )
    
    #le contenu du message
    contenu = models.TextField()

    #Est-ce que c'est le client qui à envoyé ? True = kozUser, False = commercial
    est_client = models.BooleanField(default=True)
    
    #Est-ce que le message à été lu pas le distinataire
    lu = models.BooleanField(default=True)
    
    # Date d'envoi
    date_envoi = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        #ordonne les messages du plus ancien au plus récent
        ordering = ['date_envoi']
    
    def __str__(self):
        expediteur = "client" if self.est_client else "Commercial"
        return f'{expediteur}-{self.date_envoi.strftime('%d/%m/%Y %H:%M')}'
    


