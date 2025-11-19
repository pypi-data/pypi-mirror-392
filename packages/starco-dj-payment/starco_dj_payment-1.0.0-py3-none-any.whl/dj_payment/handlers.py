from django.dispatch import receiver
from .signals import payment_verified
from utility.requesting import SyncRetryClient
import threading

def make_async_request(transaction):
    try:
        cls=SyncRetryClient()
        headers={
            'Authorization':f'Token {transaction.send_result_token}',

        }
        data = {
            'status': transaction.status == "SUCCESS",
            'uuid': transaction.uuid,
            'amount': transaction.amount
        }
        url = transaction.send_result_url
        cls.post(
            url=url,
            data=data,
            headers=headers,
            verify=False
        )
    except Exception as e:
        print(e)
@receiver(payment_verified)
def handle_successful_payment(sender, **kwargs):
    try:
        transaction = kwargs.get('transaction')
        send_result_url=transaction.send_result_url
        if send_result_url:
            print('requesting',send_result_url)
            # اجرای async در background

            t=threading.Thread(target=make_async_request,args=(transaction,))
            t.start()
            t.join()
        else:
            print('no send_result_url in transaction')
    except Exception as e:
        print(e)