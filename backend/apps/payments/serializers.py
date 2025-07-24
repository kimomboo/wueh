"""
Serializers for the payments app.
"""
from rest_framework import serializers
from django.conf import settings
from .models import Payment, PremiumSubscription
from .services import MPesaService


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""
    
    phone_number = serializers.CharField(max_length=20)
    listing_id = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = Payment
        fields = ['amount', 'premium_days', 'phone_number', 'listing_id']
    
    def validate_phone_number(self, value):
        """Validate Kenyan phone number."""
        # Remove any spaces, dashes, or plus signs
        cleaned = value.replace(' ', '').replace('-', '').replace('+', '')
        
        # Check if it's a valid Kenyan mobile number
        if not (cleaned.startswith('254') or cleaned.startswith('07') or cleaned.startswith('01')):
            raise serializers.ValidationError("Please enter a valid Kenyan mobile number.")
        
        # Convert to international format
        if cleaned.startswith('07') or cleaned.startswith('01'):
            cleaned = '254' + cleaned[1:]
        elif cleaned.startswith('254'):
            pass
        else:
            raise serializers.ValidationError("Invalid phone number format.")
        
        return cleaned
    
    def validate_premium_days(self, value):
        """Validate premium days against available plans."""
        if value not in settings.PREMIUM_PLANS:
            raise serializers.ValidationError("Invalid premium plan selected.")
        return value
    
    def validate_amount(self, value):
        """Validate amount matches premium plan."""
        premium_days = self.initial_data.get('premium_days')
        if premium_days and int(premium_days) in settings.PREMIUM_PLANS:
            expected_amount = settings.PREMIUM_PLANS[int(premium_days)]
            if float(value) != expected_amount:
                raise serializers.ValidationError(f"Amount should be {expected_amount} for {premium_days} days.")
        return value
    
    def validate(self, attrs):
        """Validate listing ownership if provided."""
        listing_id = attrs.get('listing_id')
        if listing_id:
            from apps.listings.models import Listing
            try:
                listing = Listing.objects.get(id=listing_id)
                if listing.seller != self.context['request'].user:
                    raise serializers.ValidationError("You can only upgrade your own listings.")
                attrs['listing'] = listing
            except Listing.DoesNotExist:
                raise serializers.ValidationError("Listing not found.")
        
        return attrs
    
    def create(self, validated_data):
        """Create payment and initiate M-PESA STK push."""
        user = self.context['request'].user
        listing = validated_data.pop('listing', None)
        
        # Create payment record
        payment = Payment.objects.create(
            user=user,
            listing=listing,
            payment_method='mpesa',
            status='pending',
            **validated_data
        )
        
        # Initiate M-PESA STK push
        mpesa_service = MPesaService()
        try:
            response = mpesa_service.stk_push(
                phone_number=payment.phone_number,
                amount=int(payment.amount),
                account_reference=payment.reference,
                transaction_desc=f"PeerStorm Premium - {payment.premium_days} days"
            )
            
            if response.get('ResponseCode') == '0':
                payment.mpesa_checkout_request_id = response.get('CheckoutRequestID')
                payment.status = 'processing'
                payment.save(update_fields=['mpesa_checkout_request_id', 'status'])
            else:
                payment.status = 'failed'
                payment.description = response.get('ResponseDescription', 'STK push failed')
                payment.save(update_fields=['status', 'description'])
                
        except Exception as e:
            payment.status = 'failed'
            payment.description = str(e)
            payment.save(update_fields=['status', 'description'])
        
        return payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment details."""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'reference', 'amount', 'currency', 'payment_method',
            'status', 'premium_days', 'phone_number', 'mpesa_receipt_number',
            'user_name', 'listing_title', 'description', 'created_at',
            'completed_at'
        ]
        read_only_fields = [
            'id', 'reference', 'status', 'mpesa_receipt_number',
            'created_at', 'completed_at'
        ]


class PremiumSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for premium subscriptions."""
    
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    payment_reference = serializers.CharField(source='payment.reference', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = PremiumSubscription
        fields = [
            'id', 'listing_title', 'payment_reference', 'days_purchased',
            'start_date', 'end_date', 'is_active', 'is_expired', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PremiumPlansSerializer(serializers.Serializer):
    """Serializer for premium plans."""
    
    days = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    popular = serializers.BooleanField(default=False)
    savings = serializers.CharField(required=False, allow_blank=True)
    
    def to_representation(self, instance):
        """Convert premium plans dict to serialized format."""
        days, price = instance
        
        # Mark popular plans
        popular = days in [7, 15]  # 7 and 15 days are popular
        
        # Calculate savings for longer plans
        savings = ""
        if days >= 20:
            savings = "Best Value"
        elif days == 30:
            savings = "Maximum Exposure"
        
        return {
            'days': days,
            'price': price,
            'popular': popular,
            'savings': savings
        }