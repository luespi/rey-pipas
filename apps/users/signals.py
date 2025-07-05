# apps/users/signals.py
from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.users.models import User, ClientProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Crea perfiles automáticos **solo para clientes**.
    El perfil de operador lo crea OperatorRegistrationForm.
    """
    if not created:
        return

    if instance.user_type == User.UserType.CLIENT:
        ClientProfile.objects.get_or_create(user=instance)
