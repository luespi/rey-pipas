# apps/orders/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class OperatorRequiredMixin(UserPassesTestMixin):
    """
    Permite acceder solo a usuarios cuyo `user_type` sea 'operator'.
    Reutilizado por las vistas de operador.
    """
    def test_func(self):
        return getattr(self.request.user, "user_type", None) == "operator"

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied("No eres operador.")
        return super().handle_no_permission()
