from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, ClientProfile, OperatorProfile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    • Si se crea un usuario, genera su perfil correspondiente.
    • Si se actualiza el user_type, ajusta perfil (caso raro).
    """
    if created:
        if instance.is_client:
            ClientProfile.objects.create(user=instance)
        elif instance.is_operator:
            OperatorProfile.objects.create(user=instance)
    else:
        # Por si alguien cambió el tipo a posteriori
        if instance.is_client and not hasattr(instance, "client_profile"):
            ClientProfile.objects.create(user=instance)
        if instance.is_operator and not hasattr(instance, "operator_profile"):
            OperatorProfile.objects.create(user=instance)
