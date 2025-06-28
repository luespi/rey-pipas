"""Admin personalizado para usuarios – Rey Pipas"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone

from .models import ClientProfile, OperatorProfile, User


# ──────────────────────────── USER ──────────────────────────────
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # ------------------------ Config tabla ------------------------
    list_display = (
        "username",
        "email",
        "get_full_name",
        "user_type",
        "is_verified",
        "is_active",
        "date_joined",
        "get_profile_link",
    )
    list_filter = (
        "user_type",
        "is_verified",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
    )
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"
    # 🔄 Nombres actualizados
    list_select_related = ("client_profile", "operator_profile")

    # ------------------------ Fieldsets ---------------------------
    fieldsets = UserAdmin.fieldsets + (
        (
            "Información Adicional",
            {
                "fields": (
                    "user_type",
                    "phone",
                    "address",
                    "date_of_birth",
                    "profile_image",
                    "is_verified",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Información Adicional",
            {"fields": ("email", "first_name", "last_name", "user_type", "phone")},
        ),
    )

    # ------------------------ Acciones ----------------------------
    actions = ["verify_users", "unverify_users", "activate_users", "deactivate_users"]

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = "Nombre Completo"

    def get_profile_link(self, obj):
        """
        Muestra un enlace directo para editar el perfil
        correspondente (cliente u operador) desde la lista de usuarios.
        """
        if obj.user_type == "client":
            profile = getattr(obj, "client_profile", None)
            if profile:
                url = reverse("admin:users_clientprofile_change", args=[profile.id])
                return format_html("<a href='{}'>Ver Perfil Cliente</a>", url)
        elif obj.user_type == "operator":
            profile = getattr(obj, "operator_profile", None)
            if profile:
                url = reverse("admin:users_operatorprofile_change", args=[profile.id])
                return format_html("<a href='{}'>Ver Perfil Operador</a>", url)
        return "-"

    get_profile_link.short_description = "Perfil"

    # -------------------- Filtro de visibilidad -------------------
    def get_queryset(self, request):
        """
        • Superusuarios ven todo.
        • Cualquier otro usuario NO ve:
            – cuentas superuser
            – la cuenta técnica 'admin'
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_superuser=False).exclude(username="admin")

    # ---- Bloquea acceso directo vía URL a usuarios ocultos -------
    def _deny_if_hidden(self, request, obj):
        return obj and (obj.is_superuser or obj.username == "admin") and not request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        if self._deny_if_hidden(request, obj):
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if self._deny_if_hidden(request, obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self._deny_if_hidden(request, obj):
            return False
        return super().has_delete_permission(request, obj)

    # -------------------- Acciones rápidas ------------------------
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} usuarios verificados.")
    verify_users.short_description = "Verificar usuarios seleccionados"

    def unverify_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} usuarios desverificados.")
    unverify_users.short_description = "Desverificar usuarios seleccionados"

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} usuarios activados.")
    activate_users.short_description = "Activar usuarios seleccionados"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} usuarios desactivados.")
    deactivate_users.short_description = "Desactivar usuarios seleccionados"


# ──────────────────────── CLIENT PROFILE ─────────────────────────
@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_user_email",
        "company_name",
        "total_orders",
        "total_liters",
        "get_user_phone",
        "get_user_verified",
    )
    list_filter = ("user__is_verified", "user__date_joined")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "company_name",
        "tax_id",
    )
    readonly_fields = ("total_orders", "total_liters")
    list_select_related = ("user",)

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = "Email"

    def get_user_phone(self, obj):
        return obj.user.phone
    get_user_phone.short_description = "Teléfono"

    def get_user_verified(self, obj):
        return "✓" if obj.user.is_verified else "✗"
    get_user_verified.short_description = "Verificado"


# ──────────────────────── OPERATOR PROFILE ───────────────────────
@admin.register(OperatorProfile)
class OperatorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_user_email",
        "license_number",
        "license_expiry",
        "is_active",
        "total_deliveries",
        "average_rating",
        "get_license_status",
    )
    list_filter = ("is_active", "hire_date", "license_expiry")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "license_number",
    )
    readonly_fields = ("total_deliveries", "average_rating")
    list_select_related = ("user",)

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = "Email"

    def get_license_status(self, obj):
        if obj.license_expiry <= timezone.now().date():
            color, label = "red", "Vencida"
        elif (obj.license_expiry - timezone.now().date()).days <= 30:
            color, label = "orange", "Por Vencer"
        else:
            color, label = "green", "Vigente"
        return format_html("<span style='color:{};'>⚠ {}</span>", color, label)
    get_license_status.short_description = "Estado Licencia"

    # Acciones
    actions = ["activate_operators", "deactivate_operators"]

    def activate_operators(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} operadores activados.")

    def deactivate_operators(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} operadores desactivados.")
