from django.urls import path
from . import views

urlpatterns = [
    path("transaction/", views.initiateTransactionAPI),
    path("transaction/details/", views.getTransactionAPI),
    path("pay/<str:referenceId>/", views.showPaymentPage),
    path("testing-method-1/form/", views.testing_form1),
    path("testing-method-2/form/", views.testing_form2),
    path("testing-method-3/form/", views.testing_form3),
    path("testing-maxpay-hosted/form/", views.testing_formMax),
]
