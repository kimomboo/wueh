"""
Payment models for PeerStorm Nexus Arena.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Payment(models.Model):
    """Payment records for premium upgrades."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-PESA'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
    ]
    
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # M-PESA specific fields
    phone_number = models.CharField(max_length=20, blank=True)
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    mpesa_transaction_id = models.CharField(max_length=50, blank=True)
    
    # Premium plan details
    premium_days = models.PositiveIntegerField()
    listing = models.ForeignKey(
        'listings.Listing', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='payments'
    )
    
    # Transaction details
    reference = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Callback data
    callback_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['mpesa_checkout_request_id']),
            models.Index(fields=['reference']),
        ]
    
    def __str__(self):
        return f"Payment {self.reference} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        """Override save to generate reference."""
        if not self.reference:
            self.reference = f"PSN{timezone.now().strftime('%Y%m%d')}{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)
    
    def mark_completed(self, mpesa_receipt=None, transaction_id=None):
        """Mark payment as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        if mpesa_receipt:
            self.mpesa_receipt_number = mpesa_receipt
        if transaction_id:
            self.mpesa_transaction_id = transaction_id
        
        self.save(update_fields=[
            'status', 'completed_at', 'mpesa_receipt_number', 'mpesa_transaction_id'
        ])
        
        # Upgrade listing to premium if applicable
        if self.listing:
            self.listing.make_premium(self.premium_days)
    
    def mark_failed(self, reason=None):
        """Mark payment as failed."""
        self.status = 'failed'
        if reason:
            self.description = f"{self.description}\nFailure reason: {reason}"
        self.save(update_fields=['status', 'description'])


class MPesaTransaction(models.Model):
    """M-PESA transaction records."""
    
    TRANSACTION_TYPES = [
        ('CustomerPayBillOnline', 'Customer Pay Bill Online'),
        ('CustomerBuyGoodsOnline', 'Customer Buy Goods Online'),
    ]
    
    # M-PESA fields
    merchant_request_id = models.CharField(max_length=100)
    checkout_request_id = models.CharField(max_length=100, unique=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(blank=True)
    
    # Transaction details
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Related payment
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='mpesa_transactions'
    )
    
    # Raw callback data
    raw_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'mpesa_transactions'
        verbose_name = 'M-PESA Transaction'
        verbose_name_plural = 'M-PESA Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['mpesa_receipt_number']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"M-PESA {self.checkout_request_id} - {self.result_desc}"


class PremiumSubscription(models.Model):
    """Premium subscription records."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='subscriptions')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='subscriptions')
    
    days_purchased = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'premium_subscriptions'
        verbose_name = 'Premium Subscription'
        verbose_name_plural = 'Premium Subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['listing', 'is_active']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"Premium subscription for {self.listing.title}"
    
    @property
    def is_expired(self):
        """Check if subscription is expired."""
        return timezone.now() > self.end_date
    
    def deactivate(self):
        """Deactivate subscription."""
        self.is_active = False
        self.save(update_fields=['is_active'])


class PaymentWebhook(models.Model):
    """Store webhook data for debugging."""
    
    source = models.CharField(max_length=50)  # 'mpesa', 'stripe', etc.
    event_type = models.CharField(max_length=100)
    data = models.JSONField()
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_webhooks'
        verbose_name = 'Payment Webhook'
        verbose_name_plural = 'Payment Webhooks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source', 'processed']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.source} webhook - {self.event_type}"