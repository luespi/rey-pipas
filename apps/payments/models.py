"""
Modelos de Pagos para Rey Pipas
Sistema de gestión de pagos y facturación
Actualizado según revisión 2025‑06‑02
"""

from decimal import Decimal
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """Modelo principal de pagos"""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PROCESSING = "processing", "Procesando"
        COMPLETED = "completed", "Completado"
        FAILED = "failed", "Fallido"
        CANCELLED = "cancelled", "Cancelado"
        REFUNDED = "refunded", "Reembolsado"

    class Method(models.TextChoices):
        CASH = "cash", "Efectivo"
        BANK_TRANSFER = "bank_transfer", "Transferencia Bancaria"
        OXXO = "oxxo", "OXXO"
        CREDIT_CARD = "credit_card", "Tarjeta de Crédito"
        DEBIT_CARD = "debit_card", "Tarjeta de Débito"

    # Identificación
    payment_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ID de Pago",
    )

    # Relaciones
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Pedido",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Cliente",
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payments",
        verbose_name="Procesado Por",
    )

    # Detalles del pago
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Monto",
    )
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        verbose_name="Método de Pago",
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Estado",
    )

    # Información adicional del pago
    transaction_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referencia de Transacción",
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Pago",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Vencimiento",
    )

    # Información bancaria (para transferencias)
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Banco",
    )
    account_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Número de Cuenta",
    )

    # Comprobantes
    receipt_image = models.ImageField(
        upload_to="receipts/",
        blank=True,
        null=True,
        verbose_name="Comprobante de Pago",
    )
    invoice_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Número de Factura",
    )

    # Notas
    notes = models.TextField(blank=True, verbose_name="Notas")
    failure_reason = models.TextField(blank=True, verbose_name="Razón de Fallo")

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "method"]),
            models.Index(fields=["client", "status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["payment_date"]),
        ]

    def __str__(self):
        return f"Pago {self.payment_id} - ${self.amount}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            now = timezone.now()
            self.payment_id = f"PAY{now.strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)

    # --- utilidades ---
    @property
    def is_overdue(self):
        if self.status == self.Status.PENDING and self.due_date:
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0


class Commission(models.Model):
    """Modelo de comisiones para operadores"""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        CALCULATED = "calculated", "Calculada"
        PAID = "paid", "Pagada"

    # Relaciones
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "operator"},
        related_name="commissions",
        verbose_name="Operador",
    )
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="commission",
        verbose_name="Pedido",
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="commissions",
        verbose_name="Pago",
    )

    # Cálculo de comisión
    base_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Monto Base",
    )
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        verbose_name="Porcentaje de Comisión",
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto de Comisión",
    )

    # Estado y fechas
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Estado",
    )
    calculated_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Cálculo",
    )
    paid_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Pago",
    )

    # Información de pago de comisión
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referencia de Pago",
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Comisión"
        verbose_name_plural = "Comisiones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comisión {self.operator.get_full_name()} - ${self.commission_amount}"

    def save(self, *args, **kwargs):
        # Calcular monto de comisión SIEMPRE para reflejar cambios en porcentaje
        self.commission_amount = self.base_amount * (self.commission_percentage / Decimal("100"))
        if not self.calculated_date:
            self.calculated_date = timezone.now()
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """Modelo de facturas"""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        SENT = "sent", "Enviada"
        PAID = "paid", "Pagada"
        OVERDUE = "overdue", "Vencida"
        CANCELLED = "cancelled", "Cancelada"

    # Identificación
    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Factura",
    )

    # Relaciones
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="invoice",
        verbose_name="Pedido",
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice",
        verbose_name="Pago",
    )

    # Información del cliente
    client_name = models.CharField(max_length=100, verbose_name="Nombre del Cliente")
    client_email = models.EmailField(verbose_name="Email del Cliente")
    client_address = models.TextField(verbose_name="Dirección del Cliente")
    client_tax_id = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="RFC del Cliente",
    )

    # Detalles financieros
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Impuestos")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")

    # Fechas
    issue_date = models.DateField(verbose_name="Fecha de Emisión")
    due_date = models.DateField(verbose_name="Fecha de Vencimiento")
    paid_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")

    # Estado
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Estado",
    )

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Factura {self.invoice_number} - {self.client_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            now = timezone.now()
            self.invoice_number = f"INV{now.strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)

    # --- validación ---
    def clean(self):
        if self.total_amount != self.subtotal + self.tax_amount:
            raise ValidationError("El Total debe ser igual a Subtotal + Impuestos")
