# tests/test_payments.py  (corrección ↓)
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.orders.models import Order
from apps.payments.models import Payment


# -------- fixtures mínimos --------
@pytest.fixture
def client_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username='cliente',
        email='cliente@example.com',
        password='pass',
        user_type='client'
    )


@pytest.fixture
def operator_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username='operador',
        email='operador@example.com',
        password='pass',
        user_type='operator'
    )


@pytest.fixture
def order(db, client_user, operator_user):
    return Order.objects.create(
        client=client_user,
        operator=operator_user,
        quantity_liters=1000,
        delivery_address='Calle Falsa 123',
        delivery_date='2025-07-06',
    )


# -------- test principal --------
@pytest.mark.django_db
def test_create_and_list_payment(client, client_user, order):
    Payment.objects.create(order=order, amount=150.00, method='efectivo')

    client.force_login(client_user)
    resp = client.get(reverse('payments:list'))

    assert resp.status_code == 200
    body = resp.content.decode()
    assert '150.00' in body
    assert order.order_number in body
