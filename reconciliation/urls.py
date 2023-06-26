from django.urls import path
from . import views

urlpatterns = [path("<str:referenceId>/", views.reconciliation)]
