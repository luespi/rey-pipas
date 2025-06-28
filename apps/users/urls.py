"""URLs para la aplicación de usuarios"""

from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # Autenticación
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("register/client/", views.ClientRegisterView.as_view(), name="register_client"),
    path("register/operator/", views.OperatorRegisterView.as_view(), name="register_operator"),

    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),  # ← usa la función

    # Recuperación de contraseña
    path("password-reset/", views.password_reset_request, name="password_reset"),

    # API Endpoints
    path("check-username/", views.check_username_availability, name="check_username"),
    path("check-email/", views.check_email_availability, name="check_email"),

    # Dashboard redirect
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
]