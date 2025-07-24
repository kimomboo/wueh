"""
Views for the payments app.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import json
import logging

from .models import Payment, PremiumSubscription, PaymentWebhook
from .serializers import (
    PaymentCreateSerializer, PaymentSerializer, 
    PremiumSubscriptionSerializer, PremiumPlansSerializer
)
from .services import MPesaService, PaymentAnalytics
from apps.core.utils import log_user_activity

logger = logging.getLogger(__name__)


class PremiumPlansView(generics.ListAPIView):
    """Get available premium plans."""
    
    serializer_class = PremiumPlansSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Return premium plans from settings."""
        return settings.PREMIUM_PLANS.items()
    
    def list(self, request, *args, **kwargs):
        """List premium plans."""
        plans = []
        for days, price in settings.PREMIUM_PLANS.items():
            plan_data = {
                'days': days,
                'price': price,
                'popular': days in [7, 15],  # Mark popular plans
                'savings': 'Best Value' if days >= 20 else ('Maximum Exposure' if days == 30 else '')
            }
            plans.append(plan_data)
        
        return Response(plans)


class PaymentCreateView(generics.CreateAPIView):
    """Create payment and initiate M-PESA STK push."""
    
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create payment."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment = serializer.save()
        
        # Log activity
        log_user_activity(
            user=request.user,
            activity_type='payment_initiated',
            description=f'Initiated payment for {payment.premium_days} days premium',
            metadata={
                'payment_id': str(payment.id),
                'amount': str(payment.amount),
                'premium_days': payment.premium_days
            },
            request=request
        )
        
        # Return payment details
        response_serializer = PaymentSerializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PaymentDetailView(generics.RetrieveAPIView):
    """Get payment details."""
    
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only allow users to view their own payments."""
        return Payment.objects.filter(user=self.request.user)


class PaymentListView(generics.ListAPIView):
    """List user's payments."""
    
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get current user's payments."""
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')


class UserSubscriptionsView(generics.ListAPIView):
    """List user's premium subscriptions."""
    
    serializer_class = PremiumSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get current user's subscriptions."""
        return PremiumSubscription.objects.filter(
            user=self.request.user
        ).select_related('listing', 'payment').order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_payment_status(request, payment_id):
    """Check payment status via M-PESA API."""
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not payment.mpesa_checkout_request_id:
        return Response(
            {'error': 'No M-PESA checkout request ID found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        mpesa_service = MPesaService()
        result = mpesa_service.query_transaction_status(payment.mpesa_checkout_request_id)
        
        # Update payment status based on result
        result_code = result.get('ResultCode')
        if result_code == '0':
            if payment.status != 'completed':
                payment.mark_completed()
        elif result_code in ['1032', '1037']:  # User cancelled or timeout
            payment.status = 'cancelled'
            payment.save(update_fields=['status'])
        
        return Response({
            'payment_status': payment.status,
            'mpesa_result': result
        })
        
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        return Response(
            {'error': 'Failed to check payment status'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def mpesa_callback(request):
    """Handle M-PESA callback."""
    try:
        # Log the callback
        callback_data = request.data if hasattr(request, 'data') else json.loads(request.body)
        
        # Store webhook data
        PaymentWebhook.objects.create(
            source='mpesa',
            event_type='stk_callback',
            data=callback_data
        )
        
        # Process the callback
        mpesa_service = MPesaService()
        success = mpesa_service.process_callback(callback_data)
        
        if success:
            logger.info("M-PESA callback processed successfully")
            return HttpResponse("OK", status=200)
        else:
            logger.error("Failed to process M-PESA callback")
            return HttpResponse("Error", status=400)
            
    except Exception as e:
        logger.error(f"Error in M-PESA callback: {e}")
        return HttpResponse("Error", status=500)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_analytics(request):
    """Get payment analytics for user."""
    user = request.user
    
    # User's payment stats
    user_payments = Payment.objects.filter(user=user)
    
    stats = {
        'total_spent': sum(p.amount for p in user_payments.filter(status='completed')),
        'total_payments': user_payments.count(),
        'successful_payments': user_payments.filter(status='completed').count(),
        'failed_payments': user_payments.filter(status='failed').count(),
        'pending_payments': user_payments.filter(status__in=['pending', 'processing']).count(),
    }
    
    # Premium plan usage
    plan_usage = {}
    for payment in user_payments.filter(status='completed'):
        days = payment.premium_days
        if days not in plan_usage:
            plan_usage[days] = {'count': 0, 'total_spent': 0}
        plan_usage[days]['count'] += 1
        plan_usage[days]['total_spent'] += payment.amount
    
    stats['plan_usage'] = plan_usage
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_payment(request, payment_id):
    """Cancel pending payment."""
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if payment.status not in ['pending', 'processing']:
        return Response(
            {'error': 'Can only cancel pending or processing payments'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    payment.status = 'cancelled'
    payment.save(update_fields=['status'])
    
    return Response({'message': 'Payment cancelled successfully'})


# Admin views (staff only)
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_payment_stats(request):
    """Get payment statistics for admin."""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Get date range from query params
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    analytics = PaymentAnalytics()
    
    revenue_stats = analytics.get_revenue_stats(start_date=start_date)
    success_rate = analytics.get_payment_success_rate()
    
    return Response({
        'revenue_stats': revenue_stats,
        'success_rate': success_rate,
        'date_range': {
            'start_date': start_date,
            'end_date': timezone.now(),
            'days': days
        }
    })