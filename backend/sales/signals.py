from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderStatusUpdate, OrderItem

def send_order_status_notification(order, status, note):
    # Troque por e-mail/WhatsApp/Push
    print(f"[NOTIF] Pedido #{order.id} -> {status}. Nota: {note}")

@receiver(post_save, sender=OrderStatusUpdate)
def order_status_update_notify(sender, instance: OrderStatusUpdate, created, **kwargs):
    if created:
        send_order_status_notification(instance.order, instance.status, instance.note)

@receiver(post_save, sender=OrderItem)
def recalc_order_total_on_item_save(sender, instance: OrderItem, created, **kwargs):
    instance.order.calculate_total()

@receiver(post_delete, sender=OrderItem)
def recalc_order_total_on_item_delete(sender, instance: OrderItem, **kwargs):
    instance.order.calculate_total()