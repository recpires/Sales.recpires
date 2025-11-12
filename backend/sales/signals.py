from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderStatusUpdate, OrderItem

# Funções auxiliares (Se o Order.calculate_total() salva, esta é a parte perigosa)

# Flag para evitar recursão infinita se calculate_total() chama order.save()
# Esta é a abordagem mais segura no Django.
SKIP_RECALCULATION = False

def send_order_status_notification(order, status, note):
    """
    Função para enviar notificações de mudança de status do pedido.
    (Troque por e-mail/WhatsApp/Push)
    """
    # Apenas para fins de demonstração/log
    print(f"[NOTIF] Pedido #{order.id} -> {status}. Nota: {note}")

# --- Signals para OrderStatusUpdate (Notificação) ---

@receiver(post_save, sender=OrderStatusUpdate)
def order_status_update_notify(sender, instance: OrderStatusUpdate, created, **kwargs):
    """
    Dispara notificação quando um novo status é adicionado ao pedido.
    """
    if created:
        send_order_status_notification(instance.order, instance.status, instance.note)

# --- Signals para OrderItem (Recálculo do Total) ---

@receiver(post_save, sender=OrderItem)
def recalc_order_total_on_item_save(sender, instance: OrderItem, created, **kwargs):
    """
    Recalcula o total do pedido quando um item é criado ou modificado.
    """
    global SKIP_RECALCULATION
    if SKIP_RECALCULATION:
        return

    # Protege contra recursão
    SKIP_RECALCULATION = True 
    try:
        instance.order.calculate_total()
    finally:
        SKIP_RECALCULATION = False


@receiver(post_delete, sender=OrderItem)
def recalc_order_total_on_item_delete(sender, instance: OrderItem, **kwargs):
    """
    Recalcula o total do pedido quando um item é excluído.
    """
    global SKIP_RECALCULATION
    if SKIP_RECALCULATION:
        return

    # Protege contra recursão
    SKIP_RECALCULATION = True
    try:
        instance.order.calculate_total()
    finally:
        SKIP_RECALCULATION = False