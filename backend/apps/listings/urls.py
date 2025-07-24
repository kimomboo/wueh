"""
URL configuration for listings app.
"""
from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    
    # Listings CRUD
    path('', views.ListingListView.as_view(), name='listing-list'),
    path('create/', views.ListingCreateView.as_view(), name='listing-create'),
    path('<uuid:id>/', views.ListingDetailView.as_view(), name='listing-detail'),
    path('<uuid:id>/update/', views.ListingUpdateView.as_view(), name='listing-update'),
    path('<uuid:id>/delete/', views.ListingDeleteView.as_view(), name='listing-delete'),
    
    # User listings
    path('my-listings/', views.UserListingsView.as_view(), name='user-listings'),
    
    # Special listing types
    path('hot-deals/', views.HotDealsView.as_view(), name='hot-deals'),
    path('featured/', views.FeaturedListingsView.as_view(), name='featured'),
    path('premium/', views.PremiumListingsView.as_view(), name='premium'),
    
    # Listing actions
    path('<uuid:listing_id>/contact/', views.contact_seller, name='contact-seller'),
    path('<uuid:listing_id>/report/', views.report_listing, name='report-listing'),
    path('<uuid:listing_id>/mark-sold/', views.mark_as_sold, name='mark-sold'),
    path('<uuid:listing_id>/reactivate/', views.reactivate_listing, name='reactivate'),
    
    # Search and stats
    path('search/suggestions/', views.search_suggestions, name='search-suggestions'),
    path('stats/', views.listing_stats, name='listing-stats'),
]