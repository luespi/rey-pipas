# -*- coding: utf-8 -*-
"""
Comando:
    python manage.py generate_test_orders --clients 8 --operators 3 --orders 50

• Crea usuarios tipo 'client' y 'operator' si no existen.
• A cada operador le asigna una pipa activa (Vehicle).
• Genera pedidos 'pending' en todas las zonas de forma aleatoria.

Contraseñas de prueba: 1234
"""

import random
import uuid
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from faker import Faker

from apps.orders.models import Order
from apps.vehicles.models import Vehicle

fake = Faker("es_MX")
User = get_user_model()


class Command(BaseCommand):
    help = "Genera clientes, operadores, vehículos y pedidos ficticios"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clients",
            type=int,
            default=5,
            help="Número de clientes a crear (default 5)",
        )
        parser.add_argument(
            "--operators",
            type=int,
            default=2,
            help="Número de operadores a crear (default 2)",
        )
        parser.add_argument(
            "--orders",
            type=int,
            default=30,
            help="Número de pedidos a crear (default 30)",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        n_clients   = opts["clients"]
        n_operators = opts["operators"]
        n_orders    = opts["orders"]

        # ------------------------------------------------------------------ #
        # 1. Crear clientes
        # ------------------------------------------------------------------ #
        clients = []
        for i in range(1, n_clients + 1):
            uname = f"testclient{i}"
            user, _ = User.objects.get_or_create(
                username=uname,
                defaults=dict(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=f"{uname}@example.com",
                    user_type="client",
                ),
            )
            user.set_password("1234")
            user.save(update_fields=["password"])
            clients.append(user)

        # ------------------------------------------------------------------ #
        # 2. Crear operadores y una pipa activa
        # ------------------------------------------------------------------ #
        operators = []
        for i in range(1, n_operators + 1):
            uname = f"testop{i}"
            op, _ = User.objects.get_or_create(
                username=uname,
                defaults=dict(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=f"{uname}@example.com",
                    user_type="operator",
                ),
            )
            op.set_password("1234")
            op.save(update_fields=["password"])
            operators.append(op)

            # Si no tiene vehículo activo asignado, créale uno
            if not Vehicle.objects.filter(
                assigned_operator=op, status="active"
            ).exists():
                cap = random.choice([5000, 10000, 20000])
                vehicle_type = (
                    "small"  if cap <= 5000 else
                    "medium" if cap <= 10000 else
                    "large"
                )
                today = timezone.now().date()

                Vehicle.objects.create(
                    license_plate=f"PRV-{uuid.uuid4().hex[:6].upper()}",
                    brand=random.choice(["Kenworth", "International", "Freightliner"]),
                    model=random.choice(["T800", "LT", "M2"]),
                    year=random.randint(2015, 2024),
                    vehicle_type=vehicle_type,
                    capacity_liters=cap,
                    status="active",
                    assigned_operator=op,
                    engine_number=f"ENG-{uuid.uuid4().hex[:10].upper()}",
                    chassis_number=f"CH-{uuid.uuid4().hex[:10].upper()}",
                    registration_expiry=today + timedelta(days=365),
                    insurance_expiry=today + timedelta(days=365),
                )

        # ------------------------------------------------------------------ #
        # 3. Crear pedidos pendientes
        # ------------------------------------------------------------------ #
        zones = [code for code, _ in Order.ZONES if code]  # excluye placeholder

        for _ in range(n_orders):
            Order.objects.create(
                client=random.choice(clients),
                quantity_liters=random.choice([1000, 2000, 5000, 10000]),
                delivery_address=fake.address(),
                delivery_date=timezone.now().date(),
                delivery_time_preference=random.choice(["Mañana", "Tarde"]),
                status=Order.Status.PENDING,
                priority=random.choice(Order.Priority.values),
                zone=random.choice(zones),
                colonia=fake.street_name(),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✔  Generados {n_clients} clientes, {n_operators} operadores "
                f"con pipa y {n_orders} pedidos pendientes."
            )
        )
