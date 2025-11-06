from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Store, Product, ProductVariant, Category, Coupon,
    Order, OrderItem, OrderStatusUpdate,
    Supplier, PurchaseOrder, PurchaseOrderItem # Novos modelos
)
from django.db import transaction

# --- General Serializers ---

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username', 'email')

class StoreSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ('user',)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('store',)

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('store',)

# --- Product Serializers ---

class ProductVariantSerializer(serializers.ModelSerializer):
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = '__all__'
        read_only_fields = ('product',)

    def get_stock_status(self, obj):
        if obj.stock_quantity > 10:
            return "Em Estoque"
        elif obj.stock_quantity > 0:
            return "Baixo Estoque"
        else:
            return "Esgotado"

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('store',)

# --- Order Serializers (Sales) ---

class OrderItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source='variant.__str__', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    sku = serializers.CharField(source='variant.sku', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'variant', 'quantity', 'price', 'variant_name', 'product_name', 'sku')
        read_only_fields = ('price',) # Price is set automatically

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusUpdate
        fields = '__all__'
        read_only_fields = ('order', 'timestamp')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_updates = OrderStatusUpdateSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('store', 'total_amount', 'discount_amount', 'created_at', 'updated_at')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Início da transação atômica para garantir a integridade do estoque
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            
            # Criação do primeiro status de atualização
            OrderStatusUpdate.objects.create(
                order=order, 
                old_status='', 
                new_status=order.status, 
                notes="Pedido criado"
            )

            total_amount = 0
            
            for item_data in items_data:
                variant = item_data['variant']
                quantity = item_data['quantity']
                
                if variant.stock_quantity < quantity:
                    raise serializers.ValidationError(f"Estoque insuficiente para a variante {variant.sku}. Disponível: {variant.stock_quantity}, Pedido: {quantity}.")
                
                # Cria o item do pedido, usando o preço atual da variante
                OrderItem.objects.create(
                    order=order, 
                    variant=variant, 
                    quantity=quantity,
                    price=variant.price # Captura o preço no momento da venda
                )
                
                # Diminui o estoque (Venda)
                variant.stock_quantity -= quantity
                variant.save()
                
                total_amount += variant.price * quantity

            # Aplica desconto do cupom (Lógica simplificada, o frontend deve fazer a validação)
            discount = 0.00
            if order.coupon:
                if order.coupon.type == 'PERCENTAGE':
                    discount = total_amount * (order.coupon.value / 100)
                elif order.coupon.type == 'FIXED':
                    discount = order.coupon.value
                
                order.discount_amount = min(discount, total_amount)
                total_amount -= order.discount_amount

            order.total_amount = total_amount
            order.save()
            return order

    def update(self, instance, validated_data):
        # A atualização do OrderSerializer é mais complexa, mas para o status:
        if 'status' in validated_data and instance.status != validated_data['status']:
            old_status = instance.status
            new_status = validated_data['status']
            instance.status = new_status
            instance.save()
            
            # Registro da mudança de status
            OrderStatusUpdate.objects.create(
                order=instance, 
                old_status=old_status, 
                new_status=new_status, 
                notes=f"Status alterado de {old_status} para {new_status}"
            )

        # Remove 'items' e 'status_updates' se presentes para evitar erros de atualização
        validated_data.pop('items', None)
        validated_data.pop('status_updates', None)
        
        return super().update(instance, validated_data)

# ----------------------------------------------------
#               NOVOS SERIALIZERS PARA PO
# ----------------------------------------------------

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('store',)

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source='variant.__str__', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    sku = serializers.CharField(source='variant.sku', read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ('id', 'variant', 'ordered_quantity', 'received_quantity', 'unit_cost', 'variant_name', 'product_name', 'sku', 'total_cost')
        
class PurchaseOrderSerializer(serializers.ModelSerializer):
    po_items = PurchaseOrderItemSerializer(many=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ('store', 'order_date', 'total_cost')

    def create(self, validated_data):
        po_items_data = validated_data.pop('po_items')
        
        with transaction.atomic():
            # Cria o Pedido de Compra (PO)
            purchase_order = PurchaseOrder.objects.create(**validated_data)
            
            for item_data in po_items_data:
                # O PurchaseOrderItemSerializer tem 'total_cost' como read_only. 
                # Se for passado na criação, removemos para evitar erro.
                item_data.pop('total_cost', None) 
                
                PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
            
            # Calcula o custo total após a criação dos itens
            purchase_order.calculate_total_cost()
            return purchase_order
            
    def update(self, instance, validated_data):
        po_items_data = validated_data.pop('po_items', [])
        
        # Início da transação atômica para evitar problemas de concorrência no estoque
        with transaction.atomic():
            
            # Lógica de atualização de estoque ao mudar status para RECEBIDO
            if 'status' in validated_data and validated_data['status'] in ['RECEIVED_FULL', 'RECEIVED_PARTIAL']:
                # Itera sobre os itens do PO para atualizar o estoque
                for item in instance.po_items.all():
                    # Para uma implementação segura, a lógica de recebimento de estoque é transferida
                    # para o método `receive_items` no ViewSet. O serializer apenas atualiza os campos.
                    pass
                        
            # Atualiza campos do PurchaseOrder
            instance = super().update(instance, validated_data)
            
            # Atualiza ou cria/deleta PurchaseOrderItems (para rascunhos, por exemplo)
            if po_items_data:
                
                # IDs de itens existentes
                existing_item_ids = [item.id for item in instance.po_items.all()]
                
                for item_data in po_items_data:
                    item_id = item_data.get('id')
                    
                    if item_id and item_id in existing_item_ids:
                        # Update de item existente
                        po_item = PurchaseOrderItem.objects.get(id=item_id, purchase_order=instance)
                        
                        # Se a quantidade recebida for alterada (para DRAFT/PENDING, isso é só um registro)
                        po_item.ordered_quantity = item_data.get('ordered_quantity', po_item.ordered_quantity)
                        po_item.received_quantity = item_data.get('received_quantity', po_item.received_quantity)
                        po_item.unit_cost = item_data.get('unit_cost', po_item.unit_cost)
                            
                        po_item.save()
                    elif item_id is None:
                        # Cria novo item
                        PurchaseOrderItem.objects.create(purchase_order=instance, **item_data)
                        
                # Recalcula o custo total
                instance.calculate_total_cost()
                
            return instance