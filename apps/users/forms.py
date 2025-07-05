"""
Formularios de autenticación y perfil – Rey Pipas
Incluye login, registro, edición de perfil y helpers para Cliente / Operador.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from apps.users.models import User, OperatorProfile, phone_regex
import datetime
from PIL import Image

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User, ClientProfile, OperatorProfile

# ─────────────────────────── Validadores ────────────────────────────
PHONE_REGEX = User.phone_regex  # alias del modelo

MAX_SIZE_MB   = 5     # ≤ 5 MB antes de procesar
MIN_DIMENSION = 1   # px lado corto mínimo (nitidez)
MAX_DIMENSION = 3048  # px lado largo máximo (control de gigantes)

# Clases reutilizables para <textarea>
TEXTAREA_CLASSES = (
    "textarea textarea-bordered w-full "
    "px-3 py-2 bg-white rounded-lg shadow-inner "
    "focus:outline-none focus:ring-2 focus:ring-red-500 "
    "focus:border-red-500"
)

class CustomAuthenticationForm(AuthenticationForm):
    """Login solo con correo (USERNAME_FIELD = email)"""

    username = forms.CharField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.TextInput(attrs={
            "class": (
                "w-full px-3 py-2 border rounded-md "
                "focus-primary placeholder-gray-500"
            ),
            "placeholder": "Correo electrónico",
            "autofocus": True,
        }),
    )
    ...




# ——— REGISTRO BASE (correo = USERNAME_FIELD) ———
class CustomUserCreationForm(UserCreationForm):
    """Registro universal basado en email, sin alias obligatorio"""

    email  = forms.EmailField(required=True)
    phone  = forms.CharField(max_length=17, validators=[PHONE_REGEX])

    class Meta:
        model  = User
        # username eliminado
        fields = (
            "email", "first_name", "last_name",
            "phone", "password1", "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email


# -------- Cliente --------
class ClientRegistrationForm(CustomUserCreationForm):
    address = forms.CharField(max_length=200)
    preferred_delivery_time = forms.ChoiceField(choices=[
        ("morning",  "Mañana (8-12)"),
        ("afternoon","Tarde (12-18)"),
        ("evening",  "Noche (18-22)"),
        ("flexible", "Flexible"),
    ])

    def save(self, commit=True):
            user = super().save(commit=False)
            user.user_type = User.UserType.CLIENT
            user.address   = self.cleaned_data["address"]

            # --- Generar alias si falta (parte antes de @) ---
            if not user.username:
                user.username = user.email.split("@")[0][:150]

            if commit:
                user.save()

                # Obtener o crear el perfil y actualizar campos
                profile, created = ClientProfile.objects.get_or_create(user=user)
                # Rellenar/actualizar datos específicos
                profile.preferred_delivery_time = self.cleaned_data["preferred_delivery_time"]
                profile.save()

            return user


# -------- Operador --------
class OperatorRegistrationForm(CustomUserCreationForm):
    license_number   = forms.CharField(max_length=20)
    license_expiry   = forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
    hire_date        = forms.DateField(initial=datetime.date.today,
                                       widget=forms.DateInput(attrs={"type":"date"}))
    emergency_contact_name  = forms.CharField(max_length=100)
    emergency_contact_phone = forms.CharField(max_length=17, validators=[PHONE_REGEX])

    def clean_license_expiry(self):
        expiry = self.cleaned_data["license_expiry"]
        if expiry <= datetime.date.today():
            raise ValidationError("La licencia debe estar vigente.")
        return expiry

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.UserType.OPERATOR
        if commit:
            user.save()
            OperatorProfile.objects.create(
                user=user,
                license_number   = self.cleaned_data["license_number"],
                license_expiry   = self.cleaned_data["license_expiry"],
                hire_date        = self.cleaned_data["hire_date"],
                emergency_contact_name  = self.cleaned_data["emergency_contact_name"],
                emergency_contact_phone = self.cleaned_data["emergency_contact_phone"],
            )
        return user

# ╭────────────────────── EDICIÓN DE PERFIL ───────────────────────╮
class UserProfileForm(forms.ModelForm):
    # Address como <textarea> con clases estéticas
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": TEXTAREA_CLASSES,
            "rows": 4,
        }),
        label="Dirección",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "date_of_birth",
            "profile_image",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }

    # Validar teléfono (opcional)
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            PHONE_REGEX(phone)
        return phone

    # Validar peso y dimensiones de la imagen
    def clean_profile_image(self):
        img = self.cleaned_data.get("profile_image")
        if not img:
            return img  # campo opcional

        # Peso máximo (bruto)
        if img.size > MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"La imagen debe pesar menos de {MAX_SIZE_MB} MB."
            )

        # Dimensiones mínimas y máximas
        img.file.seek(0)
        with Image.open(img.file) as im:
            w, h = im.size
            lado_corto, lado_largo = sorted((w, h))
            if lado_corto < MIN_DIMENSION:
                raise ValidationError(
                    f"La imagen es demasiado pequeña: mínimo {MIN_DIMENSION}px en el lado corto."
                )
            if lado_largo > MAX_DIMENSION:
                raise ValidationError(
                    f"La imagen es demasiado grande: máximo {MAX_DIMENSION}px en el lado largo."
                )
        return img


# ╭─────────────────── FORM EXTRA · CLIENTE ────────────────────╮
class ClientExtraForm(forms.ModelForm):
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": TEXTAREA_CLASSES,
            "rows": 4,
        }),
        label="Instrucciones especiales",
    )

    class Meta:
        model = ClientProfile
        fields = [
            "company_name",
            "tax_id",
            "preferred_delivery_time",
            "special_instructions",
        ]

# ╭─────────────────── FORM EXTRA · OPERADOR ───────────────────╮
class OperatorExtraForm(forms.ModelForm):
    class Meta:
        model = OperatorProfile
        fields = [
            "license_number",
            "license_expiry",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]





























# apps/users/forms.py
from django import forms
from django.utils import timezone
from .models import User, OperatorProfile
from .validators import phone_regex   # si ya lo tenías para clientes




from .validators import phone_regex        # importa el validador



# apps/users/forms.py
from django import forms
from django.utils import timezone

from apps.users.models import User, OperatorProfile, phone_regex


class OperatorRegistrationForm(CustomUserCreationForm):
    # ─── CAMPOS EXTRA DEL OPERADOR ────────────────────────────────────
    license_number = forms.CharField(
        max_length=30,
        label="No. de licencia de conducir",
        help_text="Obligatorio",
    )
    license_expiry = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Vencimiento de la licencia",
    )
    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Fecha de contratación",
    )
    emergency_contact_name = forms.CharField(
        max_length=80,
        label="Nombre de contacto de emergencia",
    )
    emergency_contact_phone = forms.CharField(
        validators=[phone_regex],
        label="Teléfono de emergencia",
    )

    # ─── TELÉFONO PRINCIPAL (OBLIGATORIO) ────────────────────────────
    phone = forms.CharField(
        max_length=17,
        label="Teléfono (WhatsApp)",
        validators=[phone_regex],
        help_text="7 – 15 dígitos, puede iniciar con +",
        required=True,
    )

    # qué campos mostrará el formulario
    class Meta(CustomUserCreationForm.Meta):
        model = User
        fields = (
            "first_name", "last_name", "email", "phone",
            "license_number", "license_expiry", "hire_date",
            "emergency_contact_name", "emergency_contact_phone",
            "password1", "password2",
        )

    # ─── VALIDACIÓN: LICENCIA NO CADUCADA ────────────────────────────
    def clean_license_expiry(self):
        exp = self.cleaned_data["license_expiry"]
        if exp < timezone.now().date():
            raise forms.ValidationError("La licencia ya está vencida.")
        return exp

    # ─── CREA USER + OPERATORPROFILE ─────────────────────────────────
    def save(self, commit: bool = True):
        # 1) crea el User (sin almacenarlo todavía)
        user = super().save(commit=False)
        user.user_type = User.UserType.OPERATOR
        user.phone = self.cleaned_data["phone"]

        if commit:
            # 2) guarda el usuario
            user.save()

            # 3) crea el perfil de operador enlazado
            OperatorProfile.objects.create(
                user=user,
                license_number=self.cleaned_data["license_number"],
                license_expiry=self.cleaned_data["license_expiry"],
                hire_date=self.cleaned_data["hire_date"],
                emergency_contact_name=self.cleaned_data["emergency_contact_name"],
                emergency_contact_phone=self.cleaned_data["emergency_contact_phone"],
            )
        return user
