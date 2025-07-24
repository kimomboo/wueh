"""
Admin configuration for payments app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Payment, MPesaTransaction, PremiumSubscription, PaymentWebhook


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment admin."""
    
    list_display = [
        'reference', 'user', 'amount', 'currency', 'payment_method',
        'status', 'premium_days', 'listing_link', 'created_at'
    ]
    list_filter = [
        'status', 'payment_method', 'premium_days', 'currency', 'created_at'
    ]
    search_fields = [
        'reference', 'user__email', 'user__full_name', 'phone_number',
        'mpesa_receipt_number', 'listing__title'
    ]
    raw_id_fields = ['user', 'listing']
    readonly_fields = [
        'id', 'reference', 'created_at', 'updated_at', 'completed_at',
        'mpesa_checkout_request_id', 'mpesa_receipt_number', 'mpesa_transaction_id'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('reference', 'user', 'amount', 'currency', 'payment_method', 'status')
        }),
        ('Premium Details', {
            'fields': ('premium_days', 'listing', 'description')
        }),
        ('M-PESA Details', {
            'fields': (
                'phone_number', 'mpesa_checkout_request_id', 
                'mpesa_receipt_number', 'mpesa_transaction_id'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
        ('Callback Data', {
            'fields': ('callback_data',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_failed']
    
    def listing_link(self, obj):
        """Link to listing admin."""
        if obj.listing:
            url = reverse('admin:listings_listing_change', args=[obj.listing.id])
            return format_html('<a href="{}">{}</a>', url, obj.listing.title[:50])
        return '-'
    listing_link.short_description = 'Listing'
    
    def mark_completed(self, request, queryset):
        """Mark payments as completed."""
        updated = 0
        for payment in queryset:
            if payment.status in ['pending', 'processing']:
                payment.mark_completed()
                updated += 1
        self.message_user(request, f'{updated} payments marked as completed.')
    mark_completed.short_description = 'Mark as Completed'
    
    def mark_failed(self, request, queryset):
        """Mark payments as failed."""
        updated = queryset.filter(status__in=['pending', 'processing']).update(status='failed')
        self.message_user(request, f'{updated} payments marked as failed.')
    mark_failed.short_description = 'Mark as Failed'


@admin.register(MPesaTransaction)
class MPesaTransactionAdmin(admin.ModelAdmin):
    """M-PESA Transaction admin."""
    
    list_display = [
        'checkout_request_id', 'payment_link', 'result_code', 
        'amount', 'mpesa_receipt_number', 'phone_number', 'created_at'
    ]
    list_filter = ['result_code', 'created_at']
    search_fields = [
        'checkout_request_id', 'mpesa_receipt_number', 'phone_number',
        'payment__reference'
    ]
    raw_id_fields = ['payment']
    readonly_fields = ['created_at']
    
    def payment_link(self, obj):
        """Link to payment admin."""
        if obj.payment:
            url = reverse('admin:payments_payment_change', args=[obj.payment.id])
            return format_html('<a href="{}">{}</a>', url, obj.payment.reference)
        return '-'
    payment_link.short_description = 'Payment'


@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    """Premium Subscription admin."""
    
    list_display = [
        'user', 'listing_link', 'days_purchased', 'start_date', 
        'end_date', 'is_active', 'is_expired_display'
    ]
    list_filter = ['is_active', 'days_purchased', 'created_at']
    search_fields = ['user__email', 'listing__title', 'payment__reference']
    raw_id_fields = ['user', 'listing', 'payment']
    readonly_fields = ['created_at', 'is_expired']
    
    def listing_link(self, obj):
        """Link to listing admin."""
        url = reverse('admin:listings_listing_change', args=[obj.listing.id])
        return format_html('<a href="{}">{}</a>', url, obj.listing.title[:50])
    listing_link.short_description = 'Listing'
    
    def is_expired_display(self, obj):
        """Display expiry status."""
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_expired_display.short_description = 'Status'


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    """Payment Webhook admin."""
    
    list_display = ['source', 'event_type', 'processed', 'created_at']
    list_filter = ['source', 'processed', 'created_at']
    search_fields = ['event_type', 'error_message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Webhook Info', {
            'fields': ('source', 'event_type', 'processed', 'error_message')
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )