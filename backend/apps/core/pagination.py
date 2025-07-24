"""
Custom pagination classes for PeerStorm Nexus Arena.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for most list views."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Return paginated response with additional metadata."""
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page_size,
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination for large datasets like search results."""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """Pagination for small datasets like user's items."""
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50