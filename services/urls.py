# Importing Libraries
from django.urls import path
from . import views

urlpatterns = [
    path("metrics/request-count", views.requestCounter),
    path("metrics/api-efficiency", views.apiEfficiency),
    path("metrics/db-efficiency", views.dbEfficiency),
    path("metrics/service-efficiency", views.serviceEfficiency),
    path("metrics/gateway-efficiency", views.gatewayEfficiency),
]
