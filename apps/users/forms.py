"""
Formularios de autenticación y perfil – Rey Pipas
Incluye login, registro, edición de perfil y helpers para Cliente / Operador.
"""

import datetime
import sys
from io import BytesIO
from PIL import Image

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import User, ClientProfile, OperatorProfile

# ─────────────────────────── Validadores ────────────────────────────
PHONE_REGEX = User.phone_regex                # alias del modelo
MAX_SIZE_MB = 0.3                             # 300 KB máx.
MAX_DIMENSION = 300                           # 300 px lado máx.

# ╭───────────────────────── LOGIN ─────────────────────────╮
class CustomAuthenticationForm(AuthenticationForm):
    """Formulario de login con ‘remember me’"""

    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md focus-primary placeholder-gray-500",
            "placeholder": "Email o nombre de usuario",
            "autofocus": True,
        }),
    )

    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md focus-primary placeholder-gray-500",
            "placeholder": "Contraseña",
            "autocomplete": "current-password",
        }),
    )

    remember_me = forms.BooleanField(required=False)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if "@" in username:  # login por email
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                raise ValidationError("No existe un usuario con este email.")
        return username

# ╭──────────────────────── REGISTRO BASE ─────────────────────────╮
class CustomUserCreationForm(UserCreationForm):
    """Formulario base de creación de usuarios"""

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=17, validators=[PHONE_REGEX])

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email

# ╭──────────────────── REGISTRO DE CLIENTE ─────────────────────╮
class ClientRegistrationForm(CustomUserCreationForm):
    address = forms.CharField(max_length=200)
    preferred_delivery_time = forms.ChoiceField(
        choices=[
            ("morning", "Mañana (8AM - 12PM)"),
            ("afternoon", "Tarde (12PM - 6PM)"),
            ("evening", "Noche (6PM - 10PM)"),
            ("flexible", "Flexible"),
        ]
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = "client"
        user.address = self.cleaned_data["address"]
        if commit:
            user.save()
            ClientProfile.objects.create(
                user=user,
                preferred_delivery_time=self.cleaned_data["preferred_delivery_time"],
            )
        return user

# ╭────────────────── REGISTRO DE OPERADOR ───────────────────╮
class OperatorRegistrationForm(CustomUserCreationForm):
    license_number = forms.CharField(max_length=20)
    license_expiry = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    hire_date = forms.DateField(
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={"type": "date"})
    )
    emergency_contact_name = forms.CharField(max_length=100)
    emergency_contact_phone = forms.CharField(max_length=17, validators=[PHONE_REGEX])

    def clean_license_expiry(self):
        expiry = self.cleaned_data["license_expiry"]
        if expiry <= datetime.date.today():
            raise ValidationError("La licencia debe estar vigente.")
        return expiry

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = "operator"
        if commit:
            user.save()
            OperatorProfile.objects.create(
                user=user,
                license_number=self.cleaned_data["license_number"],
                license_expiry=self.cleaned_data["license_expiry"],
                hire_date=self.cleaned_data["hire_date"],
                emergency_contact_name=self.cleaned_data["emergency_contact_name"],
                emergency_contact_phone=self.cleaned_data["emergency_contact_phone"],
            )
        return user

# ╭────────────────────── EDICIÓN DE PERFIL ───────────────────────╮
class UserProfileForm(forms.ModelForm):
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
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    # Validar teléfono (opcional)
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            PHONE_REGEX(phone)
        return phone

    # Validar y redimensionar imagen (opcional)
    def clean_profile_image(self):
        img = self.cleaned_data.get("profile_image")
        if not img:
            return img  # campo opcional

        # Peso máximo
        if img.size > MAX_SIZE_MB * 1024 * 1024:
            raise ValidationError("La imagen debe pesar menos de 300 KB.")

        # Dimensiones máximas
        image = Image.open(img)
        if max(image.size) > MAX_DIMENSION:
            output = BytesIO()
            image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
            image.save(output, format="JPEG", quality=85)
            output.seek(0)
            img = InMemoryUploadedFile(
                output,
                "ImageField",
                f"{img.name.split('.')[0]}.jpg",
                "image/jpeg",
                sys.getsizeof(output),
                None,
            )
        return img

# ╭─────────────────── FORM EXTRA · CLIENTE ────────────────────╮
class ClientExtraForm(forms.ModelForm):
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
