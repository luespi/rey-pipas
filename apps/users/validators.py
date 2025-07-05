from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r"^\+?\d{7,15}$",
    message="El teléfono debe tener entre 7 y 15 dígitos y puede iniciar con +",
)
