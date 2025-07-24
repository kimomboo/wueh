"""
WebSocket consumers for real-time notifications.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope["user"]
        
        if self.user == AnonymousUser():
            # Reject connection for anonymous users
            await self.close()
            return
        
        # Join user-specific notification group
        self.notification_group_name = f"notifications_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread count on connection
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_read':
                notification_id = text_data_json.get('notification_id')
                if notification_id:
                    await self.mark_notification_read(notification_id)
            
            elif message_type == 'get_unread_count':
                unread_count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': unread_count
                }))
                
        except json.JSONDecodeError:
            pass
    
    async def notification_message(self, event):
        """Handle notification message from group."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    async def unread_count_update(self, event):
        """Handle unread count update from group."""
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': event['count']
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notification count for user."""
        from .models import Notification
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read."""
        from .models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False


# Utility function to send real-time notifications
async def send_real_time_notification(user_id, notification_data):
    """Send real-time notification to user."""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    notification_group_name = f"notifications_{user_id}"
    
    await channel_layer.group_send(
        notification_group_name,
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )


async def update_unread_count(user_id, count):
    """Update unread count for user."""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    notification_group_name = f"notifications_{user_id}"
    
    await channel_layer.group_send(
        notification_group_name,
        {
            'type': 'unread_count_update',
            'count': count
        }
    )