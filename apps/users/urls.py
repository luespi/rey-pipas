"""URLs para la aplicación de usuarios"""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "users"

urlpatterns = [
    # Autenticación
    path("login/",  views.login_view,  name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Registro
    # Ruta principal: /users/register/  → formulario de Cliente
    path("register/", views.ClientRegisterView.as_view(), name="register"),
    # Cuando actives operadores, mantén esta:
    path("register/operator/", views.OperatorRegisterView.as_view(), name="register_operator"),

    # Perfil
    path("profile/",       views.profile_view,      name="profile"),
    path("profile/edit/",  views.profile_edit_view, name="profile_edit"),

    # Recuperación de contraseña
    path("password-reset/", views.password_reset_request, name="password_reset"),

    # API Endpoints (email únicamente)
    path("check-email/", views.check_email_availability, name="check_email"),

    # Dashboard redirect
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),

    path(
        "profile/operator-complete/",
        OperatorProfileCompleteView.as_view(),
        name="operator-profile-complete",
    )

]
