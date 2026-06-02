from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

from client_app.models import Maintenance


class Command(BaseCommand):
    help = 'Envoie des rappels de maintenance J-7'

    def handle(self, *args, **kwargs):
        date_limite = timezone.now().date() + timedelta(days=7)
        maintenances = Maintenance.objects.filter(
            date_prochaine=date_limite,
            statut='planifiee',
            rappel_envoye=False
        )
        
        for m in maintenances:
            send_mail(
                subject="🔧 Rappel : votre maintenance approche - KOZ Services",
                message=f"Bonjour {m.client.nom_complet},\n\nVotre maintenance ({m.get_type_maintenance_display()}) est prévue dans 7 jours.\nMerci de confirmer votre disponibilité.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[m.client.email],
                fail_silently=False,
            )
            m.rappel_envoye = True
            m.save()
            self.stdout.write(f"Rappel envoyé à {m.client.email}")