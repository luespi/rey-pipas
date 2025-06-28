"""
Modelo de Usuario personalizado – Rey Pipas
Sistema con roles diferenciados (cliente, operador, administrador)
"""
# ⬇️ NUEVO
from django_resized import ResizedImageField
from decimal import Decimal
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# VALIDADORES REUTILIZABLES
# ---------------------------------------------------------------------------
phone_regex = RegexValidator(
    regex=r"^\+?\d{7,15}$",
    message="El teléfono debe tener entre 7 y 15 dígitos y puede iniciar con +",
)


# ---------------------------------------------------------------------------
# CUSTOM USER MANAGER
# ---------------------------------------------------------------------------
class UserManager(BaseUserManager):
    """Gestor que respeta los roles y asegura email único"""

    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError("El campo Email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("user_type", User.UserType.CLIENT)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", User.UserType.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


# ---------------------------------------------------------------------------
# USER
# ---------------------------------------------------------------------------
class User(AbstractUser):
    """Extiende el usuario base de Django con roles y datos de contacto"""

    # Alias para compatibilidad con formularios antiguos
    phone_regex = phone_regex  # <- ¡IMPORTANTE! Mantiene User.phone_regex vigente

    class UserType(models.TextChoices):
        CLIENT = "client", "Cliente"
        OPERATOR = "operator", "Operador"
        ADMIN = "admin", "Administrador"

    # -------------------- Contacto --------------------
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Teléfono", validators=[phone_regex], max_length=17, blank=True)

    # -------------------- Rol --------------------
    user_type = models.CharField(
        "Tipo de Usuario",
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
        db_index=True,
    )

    # -------------------- Datos opcionales --------------------
    address = models.TextField("Dirección", blank=True)
    date_of_birth = models.DateField("Fecha de Nacimiento", null=True, blank=True)
    # ⬇️ SUSTITUIDO
    # profile_image = models.ImageField("Foto de Perfil", upload_to="profiles/", null=True, blank=True)
    profile_image = ResizedImageField(
        "Foto de Perfil",
        size=[512, 512],         # máx. 512 × 512 px
        quality=80,              # compresión JPEG
        force_format="JPEG",     # convierte PNG/WebP → JPEG
        upload_to="profiles/",
        null=True,
        blank=True,
    )

    # …

    # -------------------- Metadatos --------------------
    created_at = models.DateTimeField("Fecha de Creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última Actualización", auto_now=True)
    is_verified = models.BooleanField("Verificado", default=False)

    # Gestor por defecto
    objects = UserManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user_type", "is_active"])]
        constraints = [models.UniqueConstraint(fields=["email"], name="unique_email")]

    # -------------------- Utilidades --------------------
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"

    def get_full_name(self) -> str:  # type: ignore[override]
        name = super().get_full_name().strip()
        return name or self.username

    @property
    def is_client(self) -> bool:
        return self.user_type == self.UserType.CLIENT

    @property
    def is_operator(self) -> bool:
        return self.user_type == self.UserType.OPERATOR

    @property
    def is_admin_user(self) -> bool:
        return self.user_type == self.UserType.ADMIN


# ---------------------------------------------------------------------------
# CLIENT PROFILE
# ---------------------------------------------------------------------------
class ClientProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": User.UserType.CLIENT},
        related_name="client_profile",
        verbose_name="Usuario",
    )

    company_name = models.CharField("Nombre de Empresa", max_length=100, blank=True)
    tax_id = models.CharField("RFC/CURP", max_length=20, blank=True)

    preferred_delivery_time = models.CharField("Horario Preferido", max_length=50, blank=True)
    special_instructions = models.TextField("Instrucciones Especiales", blank=True)

    total_orders = models.PositiveIntegerField("Total de Pedidos", default=0)
    total_liters = models.PositiveIntegerField("Total de Litros", default=0)  # litros completos

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Cliente"
        verbose_name_plural = "Perfiles de Clientes"

    def __str__(self):
        return f"Cliente · {self.user.get_full_name() or self.user.username}"


# ---------------------------------------------------------------------------
# OPERATOR PROFILE
# ---------------------------------------------------------------------------
class OperatorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": User.UserType.OPERATOR},
        related_name="operator_profile",
        verbose_name="Usuario",
    )

    license_number = models.CharField("Número de Licencia", max_length=20, unique=True)
    license_expiry = models.DateField("Vencimiento de Licencia", db_index=True)

    is_active = models.BooleanField("Activo", default=True)
    hire_date = models.DateField("Fecha de Contratación")

    total_deliveries = models.PositiveIntegerField("Total de Entregas", default=0)
    average_rating = models.DecimalField(
        "Calificación Promedio", max_digits=3, decimal_places=2, default=Decimal("0.00")
    )

    emergency_contact_name = models.CharField("Contacto de Emergencia", max_length=100)
    emergency_contact_phone = models.CharField(
        "Teléfono de Emergencia", max_length=17, validators=[phone_regex]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Operador"
        verbose_name_plural = "Perfiles de Operadores"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["license_expiry"]),
        ]

    def __str__(self):
        return f"Operador · {self.user.get_full_name() or self.user.username}"

    # -------- utilidades extra --------
    @property
    def days_until_license_expiry(self) -> int:
        """Días faltantes para que caduque la licencia"""
        return (self.license_expiry - timezone.now().date()).days
