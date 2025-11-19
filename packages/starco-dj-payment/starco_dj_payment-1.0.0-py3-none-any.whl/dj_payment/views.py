from django.shortcuts import get_object_or_404
from .models import  PaymentTransaction
from django.shortcuts import render
from .services import PaymentService
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .signals import payment_verified
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

def redirect_to_pay(request,short_id:str):
    transaction=get_object_or_404(PaymentTransaction, short_id=short_id)
    if transaction.status != 'SUCCESS':
        context = {
            'status': True,
            'url':transaction.gateway_payment_url,
            'error':'',
        }
    elif transaction.status == 'SUCCESS':
        context = {
            'status': False,
            'url': '',
            'error': 'این تراکنش قبلا پرداخت شده است.',
        }
    else:
        context = {
            'status':False,
            'url':'',
            'error': 'خطا در پرداخت، مجددا اقدام کنید.',
        }
    response= render(request, 'payment/redirect_to_gateway.html', context)
    return response


@method_decorator(csrf_exempt, name='dispatch')
class CallbackTemplateView(TemplateView):
    template_name = 'payment/callback.html'
    def callback(self, context,short_id, requset_method:dict):
        transaction = get_object_or_404(PaymentTransaction, short_id=short_id)
        response={k:(v[0] if isinstance(v,list) else v) for k,v in dict(requset_method).items()}
        PaymentService.verify_payment(transaction,response)
        return HttpResponseRedirect(transaction.user_callback_url)


    def get(self, request,short_id:str, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.callback(context,short_id, self.request.GET)

    def post(self, request,short_id:str, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.callback(context,short_id, self.request.POST)


#####################################################################
