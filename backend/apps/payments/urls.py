"""
URL configuration for payments app.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Premium plans
    path('plans/', views.PremiumPlansView.as_view(), name='premium-plans'),
    
    # Payments
    path('create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<uuid:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('<uuid:payment_id>/status/', views.check_payment_status, name='payment-status'),
    path('<uuid:payment_id>/cancel/', views.cancel_payment, name='payment-cancel'),
    
    # Subscriptions
    path('subscriptions/', views.UserSubscriptionsView.as_view(), name='user-subscriptions'),
    
    # Analytics
    path('analytics/', views.payment_analytics, name='payment-analytics'),
    
    # M-PESA callback
    path('mpesa/callback/', views.mpesa_callback, name='mpesa-callback'),
    
    # Admin endpoints
    path('admin/stats/', views.admin_payment_stats, name='admin-payment-stats'),
]