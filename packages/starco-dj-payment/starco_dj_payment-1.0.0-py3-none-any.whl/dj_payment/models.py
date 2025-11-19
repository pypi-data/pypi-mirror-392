from django.db import models
from django.contrib.auth import get_user_model
import uuid
import datetime

class PaymentGateway(models.Model):
    name = models.CharField(max_length=100)
    gateway_name = models.CharField(max_length=50, choices=[
        ('VANDAR', 'وندار'),
        ('NOVINPAL', 'نوین پال'),
        ('AQAYEPARDAKHT', 'آقای پرداخت'),
        ('ZARINPAL', 'زرین‌پال'),
        ('IDPAY', 'آیدی پی'),
        ('NEXTPAY', 'نکست‌پی'),
        ('PAYPING', 'پی‌پینگ'),
        ('SIZPAY', 'سیزپی'),

    ])
    is_active = models.BooleanField(default=True)
    merchant_id = models.CharField(max_length=100)
    api_key = models.CharField(max_length=100,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    test_mode = models.BooleanField(default=False, verbose_name='حالت تست')
    priority = models.PositiveSmallIntegerField(default=0, verbose_name='اولویت')

    class Meta:
        # verbose_name = 'درگاه پرداخت'
        # verbose_name_plural = 'درگاه‌های پرداخت'
        ordering = ['-priority', 'name']
    def __str__(self):
        return self.name

class PaymentTransaction(models.Model):


    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='payment_transactions'
    )
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    short_id = models.CharField(max_length=150, editable=False, unique=True)
    status_list=[
        ('PENDING', 'در انتظار پرداخت'),
        ('SUCCESS', 'موفق'),
        ('FAILED', 'ناموفق'),
        ('CANCELED', 'لغو شده'),
    ]
    input_currency = models.CharField(max_length=10, default='IRT')
    status = models.CharField(max_length=20, choices=status_list)
    description = models.TextField(blank=True, null=True)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    bank = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    error_message=models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ##################################
    gateway_token = models.CharField(max_length=100)
    gateway_payment_url = models.URLField(null=True, blank=True)
    ##################################
    user_token = models.CharField(max_length=100, editable=False, unique=True)
    user_callback_url = models.CharField(max_length=255, null=True, blank=True)
    test_mode = models.BooleanField(default=False, verbose_name='حالت تست')
    ##################################
    @staticmethod
    def generate_token():
        return str(uuid.uuid4())

    @staticmethod
    def generate_short_id():
        import random
        import string
        # Get timestamp as base
        base = str(int(datetime.datetime.now().timestamp()))
        # Add random uppercase letters
        letters = ''.join(random.choices(string.ascii_lowercase, k=len(base)))
        # Combine and shuffle
        combined = [num + letters[i] for i, num in enumerate(base)]
        return ''.join(combined)
    @classmethod
    def create_transaction(
            cls,
            user,
            gateway:PaymentGateway,
            amount:int,
            user_callback_url:str,
            phone:str,
            email:str,
            description:str=None,
            input_currency:str='IRT',
            test_mode=False,
    ):
        short_id = cls.generate_short_id()
        user_token = cls.generate_token()
        status = 'PENDING'
        transaction = PaymentTransaction(
            gateway=gateway,
            user=user,
            amount=amount,
            short_id=short_id,
            user_token=user_token,
            user_callback_url=user_callback_url,
            status=status,
            phone=phone,
            email=email,
            input_currency=input_currency,
            description=description,
            test_mode=test_mode,

        )
        transaction.save()
        return transaction
    def __str__(self):
        return f"PaymentTransaction {self.id}"
