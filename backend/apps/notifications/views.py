"""
Views for the notifications app.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from .models import Notification, SystemAnnouncement, NotificationPreference
from .serializers import (
    NotificationSerializer, SystemAnnouncementSerializer,
    NotificationPreferenceSerializer, NotificationStatsSerializer
)


class NotificationListView(generics.ListAPIView):
    """List user notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get current user's notifications."""
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('listing').order_by('-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    """Get notification details and mark as read."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only allow users to view their own notifications."""
        return Notification.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Get notification and mark as read."""
        notification = self.get_object()
        notification.mark_as_read()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


class SystemAnnouncementListView(generics.ListAPIView):
    """List active system announcements."""
    
    serializer_class = SystemAnnouncementSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get active announcements."""
        now = timezone.now()
        return SystemAnnouncement.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('-created_at')


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """Get and update notification preferences."""
    
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create notification preferences for current user."""
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark specific notification as read."""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    updated = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return Response({
        'message': f'{updated} notifications marked as read'
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_notification(request, notification_id):
    """Delete specific notification."""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.delete()
        return Response({'message': 'Notification deleted'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_all_notifications(request):
    """Clear all notifications for user."""
    deleted = Notification.objects.filter(user=request.user).delete()[0]
    
    return Response({
        'message': f'{deleted} notifications cleared'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """Get notification statistics."""
    user = request.user
    
    # Get counts
    total = Notification.objects.filter(user=user).count()
    unread = Notification.objects.filter(user=user, is_read=False).count()
    read = total - unread
    
    # Get notifications by type
    type_counts = Notification.objects.filter(user=user).values(
        'notification_type'
    ).annotate(count=Count('id')).order_by('-count')
    
    notifications_by_type = {
        item['notification_type']: item['count'] 
        for item in type_counts
    }
    
    # Get recent notifications
    recent = Notification.objects.filter(user=user).order_by('-created_at')[:5]
    
    stats = {
        'total_notifications': total,
        'unread_notifications': unread,
        'read_notifications': read,
        'notifications_by_type': notifications_by_type,
        'recent_notifications': NotificationSerializer(recent, many=True).data
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """Get unread notification count."""
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return Response({'unread_count': count})