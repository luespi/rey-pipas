"""
Vistas de autenticación y perfil – Rey Pipas
"""
# añade el import arriba
from .forms import OperatorRegistrationForm

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db import transaction
from django.db.models import Sum          # <-- NUEVO


from .forms import (
    ClientRegistrationForm,
    CustomAuthenticationForm,
    OperatorRegistrationForm,
    UserProfileForm,
    ClientExtraForm,
    OperatorExtraForm,
)
from .models import ClientProfile, OperatorProfile, User

# -------------------- Funciones --------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if form.cleaned_data.get("remember_me"):
                request.session.set_expiry(1209600)  # 2 semanas
            messages.success(request, f"¡Bienvenido, {user.get_full_name()}!")
            return redirect(request.GET.get("next") or "dashboard")
        messages.error(request, "Credenciales inválidas.")
    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect("home")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    user_type = request.GET.get("type", "client")
    form_class = {
        "client": ClientRegistrationForm,
        "operator": OperatorRegistrationForm,
    }.get(user_type, ClientRegistrationForm)

    form = form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
                login(request, user)
                messages.success(request, "¡Cuenta creada exitosamente!")
                return redirect("dashboard")
        except Exception as e:
            messages.error(request, f"Error al crear la cuenta: {e}")
    return render(request, "auth/register.html", {"form": form, "user_type": user_type})







@login_required
def profile_view(request):
    """
    Muestra el perfil del usuario y permite actualizar sus datos básicos.
    Además calcula métricas de pedidos y litros reales cuando el usuario es cliente.
    """
    user = request.user

    # ---------- Formulario principal ----------
    form = UserProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=user
    )

    # Guardar cambios básicos (nombre, teléfono, foto, etc.)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil actualizado exitosamente.")
        return redirect("users:profile")

    # ---------- Métricas de pedidos ----------
    orders_count  = 0
    total_liters  = 0
    if user.is_client:
        from apps.orders.models import Order        # import local (evita circular)
        orders_qs = Order.objects.filter(client=user)
        orders_count = orders_qs.count()
        total_liters = orders_qs.aggregate(l=Sum("quantity_liters"))["l"] or 0


    # ---------- Perfil extra ----------
    profile = None
    if user.is_client:
        profile, _ = ClientProfile.objects.get_or_create(user=user)
    elif user.is_operator:
        profile, _ = OperatorProfile.objects.get_or_create(user=user)

    # ---------- Render ----------
    return render(
        request,
        "auth/profile.html",
        {
            "form": form,
            "profile": profile,
            "user": user,
            "orders_count": orders_count,
            "total_liters": total_liters,
        },
    )







# ─────────────────────────────────────────────────────────────
#  Vista funcional para editar perfil (opción B)
# ─────────────────────────────────────────────────────────────

@login_required
def profile_edit_view(request):
    """Formulario para editar el usuario + su perfil extra (cliente / operador)."""

    user = request.user

    # ---------- Form principal (User) ----------
    user_form = UserProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=user,
    )

    # ---------- Form extra ----------
    extra_form = None
    if user.is_client:
        extra_instance, _ = ClientProfile.objects.get_or_create(user=user)
        extra_form = ClientExtraForm(request.POST or None, instance=extra_instance)
    elif user.is_operator:
        extra_instance, _ = OperatorProfile.objects.get_or_create(user=user)
        extra_form = OperatorExtraForm(request.POST or None, instance=extra_instance)

    # ---------- Guardar ----------
    if request.method == "POST":
        forms_valid = user_form.is_valid() and (extra_form is None or extra_form.is_valid())
        if forms_valid:
            user_form.save()
            if extra_form:
                extra_form.save()
            messages.success(request, "Perfil actualizado exitosamente ✔️")
            return redirect("users:profile")
        else:
            messages.error(request, "Corrige los errores resaltados.")

    # ---------- Render ----------
    return render(request, "auth/profile_edit.html", {
        "user_form": user_form,
        "extra_form": extra_form,
    })


@login_required
def dashboard_redirect(request):
    return redirect("dashboard")


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        # TODO: implementar envío de correo real
        messages.success(request, "Se ha enviado un enlace de restablecimiento a tu correo.")
    return render(request, "auth/password_reset.html")


# -------------------- AJAX --------------------

def check_username_availability(request):
    username = request.GET.get("username")
    return JsonResponse({"available": username and not User.objects.filter(username=username).exists()})


def check_email_availability(request):
    email = request.GET.get("email")
    return JsonResponse({"available": email and not User.objects.filter(email=email).exists()})


# -------------------- CBV para registro --------------------

class ClientRegisterView(CreateView):
    model = User
    form_class = ClientRegistrationForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "¡Cuenta de cliente creada exitosamente!")
        return response


class OperatorRegisterView(CreateView):
    model = User
    form_class = OperatorRegistrationForm
    template_name = "auth/operator_register.html"
    success_url = reverse_lazy("dashboard")   # ← destino final lógico

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)      # lo logueas una sola vez
        messages.success(self.request, "¡Cuenta de operador creada exitosamente!")
        return response
