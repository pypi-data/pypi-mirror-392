from django.urls import reverse
from .gateways import Gateway
from .models import PaymentTransaction, PaymentGateway
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentService:
    def __init__(self):
        self.active_gateways = PaymentGateway.objects.filter(is_active=True).order_by('-priority')

    def get_available_gateways(self):
        return self.active_gateways.all()

    def get_available_gateway(self, preferred_gateway_id=None):
        if preferred_gateway_id:
            gateway = self.active_gateways.filter(
                id=preferred_gateway_id,

            ).first()
            if gateway:
                return gateway
        # اگر درگاه ترجیحی در دسترس نبود، درگاه بعدی بر اساس اولویت انتخاب می‌شود
        gateway = self.active_gateways.first()
        if not gateway:
            raise Exception('درگاه پرداخت در دسترس نیست')
        return gateway

    @staticmethod
    def gateway(transaction: PaymentTransaction) -> Gateway:
        selected_gate = transaction.gateway
        gateway_name = selected_gate.gateway_name
        merchant_id = selected_gate.merchant_id
        api_key = selected_gate.api_key
        test_mode = selected_gate.test_mode or transaction.test_mode
        input_currency = transaction.input_currency
        print("test_mode",test_mode)
        gateway = Gateway(
            gateway_name=gateway_name,
            merchant_id=merchant_id,
            api_key=api_key,
            input_currency=input_currency,
            test_mode=test_mode
        )
        return gateway

    @staticmethod
    def payment_url(request, short_id: str):
        base_url = request.build_absolute_uri('/')
        base_url = base_url.replace('http://', 'https://')
        return base_url.rstrip('/') + reverse('payment:redirect_to_pay', kwargs={'short_id': short_id})

    @staticmethod
    def process_payment_from_gateway(request, transaction: PaymentTransaction) -> dict:
        """مرحله 2: ارسال به درگاه پرداخت"""
        amount = transaction.amount
        short_id = transaction.short_id
        base_url = request.build_absolute_uri('/').rstrip('/')
        callback = base_url + reverse('payment:callback', kwargs={'short_id': short_id})
        mobile = transaction.phone
        email = transaction.email
        description = f'پرداخت سفارش {short_id}'
        gateway = PaymentService.gateway(transaction)
        gateway_result = gateway.paylink(
            amount,
            callback,
            mobile=mobile,
            email=email,
            description=description
        )

        return gateway_result

    @staticmethod
    def verify_payment(transaction: PaymentTransaction, response: dict) -> dict:
        """مرحله 3: تایید پرداخت"""

        gateway = PaymentService.gateway(transaction)

        transaction_dict = {
            'gateway_token': transaction.gateway_token,
            'amount': transaction.amount,

        }
        params = gateway.gateway.callback_params(response, transaction_dict)
        status, data = gateway.verify(**params)
        if status:
            transaction.status = 'SUCCESS'
            transaction.card_number = params.get('card_number')
            transaction.bank = params.get('bank')
            transaction.save()
            return {
                'status': True,
                'error': '',
                'transaction': transaction,
            }
        else:
            error_message = gateway.gateway.error_message(data)
            transaction.status = 'FAILED'
            transaction.error_message = error_message
            transaction.save()
            return {
                'status': False,
                'error': error_message,
                'transaction': transaction,
            }

    def cancel_transaction(self, uuid: str) -> PaymentTransaction:
        """مرحله اختیاری: لغو تراکنش"""

        transaction = PaymentTransaction.objects.get(uuid=uuid)
        transaction.status = 'CANCELED'
        transaction.save()
        return transaction
