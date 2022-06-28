import hmac
import hashlib
from django.conf import settings

def verify_webhook(request):
	secret=bytes(settings.PAYSTACK_SECRET, "utf-8")
	digester = hmac.new(secret, request.body, hashlib.sha512)
	calculated_signature = digester.hexdigest()

	if calculated_signature == request.META['HTTP_X_PAYSTACK_SIGNATURE']:
		return True
	return False