import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


@pytest.fixture
def seed(db, django_user_model):
    """Seed 3 operators, 3 clients, their vehicles y 3 pedidos."""

    # --- Operadores ---
    ops = [
        django_user_model.objects.create_user(
            email=f"op{i}@example.com",
            password="Passw0rd!",
            first_name=f"Op{i}",
            user_type="operator",
        )
        for i in range(1, 4)
    ]

    # --- Clientes ---
    clients = [
        django_user_model.objects.create_user(
            email=f"cli{i}@example.com",
            password="Passw0rd!",
            first_name=f"Cli{i}",
            user_type="client",
        )
        for i in range(1, 4)
    ]

    # --- Vehículos (todos los NOT NULL cubiertos) ---
    from apps.vehicles.models import Vehicle

    for op in ops:
        Vehicle.objects.create(
            assigned_operator=op,
            license_plate=f"TEST-{op.id}",
            brand="TestBrand",
            model="TestModel",
            vehicle_type=Vehicle.VehicleType.SMALL,
            year=timezone.now().year,
            capacity_liters=10000,
            status=Vehicle.Status.ACTIVE,
            engine_number=f"ENG-{op.id}",
            chassis_number=f"CH-{op.id}",
            registration_expiry=timezone.now().date() + timedelta(days=365),
            insurance_expiry=timezone.now().date() + timedelta(days=365),
        )

    # --- Pedidos pendientes ---
    from apps.orders.models import Order

    for idx, cli in enumerate(clients, start=1):
        Order.objects.create(
            client=cli,
            quantity_liters=1000 * idx,
            status=Order.Status.PENDING,
            delivery_address=f"Calle Falsa #{100+idx}",
            delivery_date=timezone.now().date() + timedelta(days=idx),
        )

    return {"ops": ops, "clients": clients}


@pytest.mark.django_db
def test_operator_flow(client, seed):
    op1, op2 = seed["ops"][:2]

    from apps.orders.models import Order

    # 1️⃣ op1 acepta primer pedido
    client.login(email=op1.email, password="Passw0rd!")
    order1 = Order.objects.first()
    client.post(reverse("orders_operator:accept", args=[order1.pk]))
    order1.refresh_from_db()
    assert order1.status == Order.Status.ASSIGNED
    assert order1.operator == op1

    # 2️⃣ op1 marca entregado
    client.post(reverse("orders_operator:deliver", args=[order1.pk]))
    order1.refresh_from_db()
    assert order1.status == Order.Status.DELIVERED

    # 3️⃣ op1 acepta pedido 2 y luego rechaza
    order2 = Order.objects.filter(status=Order.Status.PENDING).first()
    client.post(reverse("orders_operator:accept", args=[order2.pk]))
    client.post(reverse("orders_operator:reject", args=[order2.pk]))
    order2.refresh_from_db()
    assert order2.status == Order.Status.PENDING
    assert order2.operator is None

    # 4️⃣ op2 acepta pedido restante
    client.logout()
    client.login(email=op2.email, password="Passw0rd!")
    order3 = Order.objects.filter(status=Order.Status.PENDING).first()
    client.post(reverse("orders_operator:accept", args=[order3.pk]))
    order3.refresh_from_db()
    assert order3.status == Order.Status.ASSIGNED
    assert order3.operator == op2
