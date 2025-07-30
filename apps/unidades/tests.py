from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.unidades.models import Unidad
from apps.orders.models import Order

User = get_user_model()

class UnidadFlowTests(TestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            email="chofer@example.com",
            password="pass",
            user_type=User.UserType.OPERATOR
        )
        self.client.login(email="chofer@example.com", password="pass")

    def test_operator_creates_unidad(self):
        resp = self.client.post(reverse("unidades:create"), {
            "numero_placas": "ABC123",
            "capacidad_litros": 10000,
            # imágenes opcionales omitidas en test
        })
        self.assertRedirects(resp, reverse("unidades:list"))
        unidad = Unidad.objects.get(numero_placas="ABC123")
        self.assertEqual(unidad.assigned_operator, self.operator)

    def test_unidad_assigned_on_accept(self):
        unidad = Unidad.objects.create(
            numero_placas="ABC123", capacidad_litros=10000,
            assigned_operator=self.operator
        )
        order = Order.objects.create(
            client=self.operator,  # simplificación de prueba
            quantity_liters=2000,
            delivery_address="X",
            zone="AO",
            colonia="Centro",
            delivery_date="2030-01-01"
        )
        # Simulamos POST a la vista de aceptar
        self.client.post(reverse("orders_operator:accept", args=[order.pk]))
        order.refresh_from_db()
        self.assertEqual(order.unidad, unidad)
