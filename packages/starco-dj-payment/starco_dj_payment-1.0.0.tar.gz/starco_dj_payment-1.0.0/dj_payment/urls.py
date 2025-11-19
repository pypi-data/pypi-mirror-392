from django.urls import path
from .views import *
from .api.views import *
app_name='payment'

urlpatterns = [
    path('gateways/', PaymentGatewayListAPI.as_view(), name='payment-gateways'),
    path('create/', CreateTransactionAPI.as_view(), name='create-transaction'),
    path('pay/<str:short_id>/', redirect_to_pay, name='redirect_to_pay'),
    path('callback/<str:short_id>/', CallbackTemplateView.as_view(), name='callback'),
    path('verify/', VerifyTransactionAPI.as_view(), name='verify-transaction'),

]
