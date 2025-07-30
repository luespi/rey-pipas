# apps/unidades/urls.py


from django.urls import path
from .views import UnidadCreateView, UnidadListView
from .views import UnidadUpdateView

app_name = "unidades"

urlpatterns = [
    path("", UnidadListView.as_view(), name="list"),
    path("nueva/", UnidadCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", UnidadUpdateView.as_view(), name="update"),
]


