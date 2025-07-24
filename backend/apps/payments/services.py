"""
Payment services for PeerStorm Nexus Arena.
"""
import requests
import base64
from datetime import datetime
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class MPesaService:
    """M-PESA Daraja API service."""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        
        # Set API URLs based on environment
        if settings.MPESA_ENVIRONMENT == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """Get M-PESA access token."""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        # Create basic auth header
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('access_token')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get M-PESA access token: {e}")
            raise Exception(f"Failed to get access token: {e}")
    
    def generate_password(self):
        """Generate M-PESA password."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()
        return password, timestamp
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK push."""
        access_token = self.get_access_token()
        password, timestamp = self.generate_password()
        
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Ensure phone number is in correct format
        if phone_number.startswith('254'):
            phone_number = phone_number
        elif phone_number.startswith('07') or phone_number.startswith('01'):
            phone_number = '254' + phone_number[1:]
        else:
            raise ValueError("Invalid phone number format")
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"STK push initiated: {data}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"STK push failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise Exception(f"STK push failed: {e}")
    
    def query_transaction_status(self, checkout_request_id):
        """Query transaction status."""
        access_token = self.get_access_token()
        password, timestamp = self.generate_password()
        
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Transaction status query: {data}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Transaction status query failed: {e}")
            raise Exception(f"Status query failed: {e}")
    
    def process_callback(self, callback_data):
        """Process M-PESA callback data."""
        from .models import Payment, MPesaTransaction
        
        try:
            # Extract callback data
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            merchant_request_id = stk_callback.get('MerchantRequestID')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Create or update M-PESA transaction record
            mpesa_transaction, created = MPesaTransaction.objects.get_or_create(
                checkout_request_id=checkout_request_id,
                defaults={
                    'merchant_request_id': merchant_request_id,
                    'result_code': result_code,
                    'result_desc': result_desc,
                    'raw_data': callback_data
                }
            )
            
            # Find related payment
            try:
                payment = Payment.objects.get(mpesa_checkout_request_id=checkout_request_id)
                mpesa_transaction.payment = payment
                mpesa_transaction.save()
                
                if result_code == 0:  # Success
                    # Extract transaction details
                    callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    
                    amount = None
                    mpesa_receipt = None
                    transaction_date = None
                    phone_number = None
                    
                    for item in callback_metadata:
                        name = item.get('Name')
                        value = item.get('Value')
                        
                        if name == 'Amount':
                            amount = value
                        elif name == 'MpesaReceiptNumber':
                            mpesa_receipt = value
                        elif name == 'TransactionDate':
                            transaction_date = datetime.strptime(str(value), '%Y%m%d%H%M%S')
                        elif name == 'PhoneNumber':
                            phone_number = value
                    
                    # Update M-PESA transaction
                    mpesa_transaction.amount = amount
                    mpesa_transaction.mpesa_receipt_number = mpesa_receipt
                    mpesa_transaction.transaction_date = transaction_date
                    mpesa_transaction.phone_number = phone_number
                    mpesa_transaction.save()
                    
                    # Mark payment as completed
                    payment.mark_completed(
                        mpesa_receipt=mpesa_receipt,
                        transaction_id=checkout_request_id
                    )
                    
                    logger.info(f"Payment {payment.reference} completed successfully")
                    
                else:  # Failed
                    payment.mark_failed(result_desc)
                    logger.warning(f"Payment {payment.reference} failed: {result_desc}")
                
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for checkout request: {checkout_request_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing M-PESA callback: {e}")
            return False


class PaymentAnalytics:
    """Payment analytics service."""
    
    @staticmethod
    def get_revenue_stats(start_date=None, end_date=None):
        """Get revenue statistics."""
        from .models import Payment
        from django.db.models import Sum, Count, Avg
        
        queryset = Payment.objects.filter(status='completed')
        
        if start_date:
            queryset = queryset.filter(completed_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(completed_at__lte=end_date)
        
        stats = queryset.aggregate(
            total_revenue=Sum('amount'),
            total_transactions=Count('id'),
            average_transaction=Avg('amount')
        )
        
        # Premium plan breakdown
        plan_stats = queryset.values('premium_days').annotate(
            count=Count('id'),
            revenue=Sum('amount')
        ).order_by('-count')
        
        return {
            'total_revenue': stats['total_revenue'] or 0,
            'total_transactions': stats['total_transactions'] or 0,
            'average_transaction': stats['average_transaction'] or 0,
            'plan_breakdown': list(plan_stats)
        }
    
    @staticmethod
    def get_payment_success_rate():
        """Get payment success rate."""
        from .models import Payment
        from django.db.models import Count, Case, When, IntegerField
        
        stats = Payment.objects.aggregate(
            total=Count('id'),
            successful=Count(Case(When(status='completed', then=1))),
            failed=Count(Case(When(status='failed', then=1))),
            pending=Count(Case(When(status__in=['pending', 'processing'], then=1)))
        )
        
        total = stats['total']
        if total > 0:
            success_rate = (stats['successful'] / total) * 100
        else:
            success_rate = 0
        
        return {
            'success_rate': round(success_rate, 2),
            'total_payments': total,
            'successful_payments': stats['successful'],
            'failed_payments': stats['failed'],
            'pending_payments': stats['pending']
        }