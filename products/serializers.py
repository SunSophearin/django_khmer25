from decimal import Decimal
from rest_framework import serializers
from .models import Category, Product, Cart, CartItem

# ----------------------------
# Category Serializer (Nested)
# ----------------------------
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "image"]


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "image", "slug", "parent", "subcategories"]


# -----------------------------------------
# Small serializer for "Related Products"
# -----------------------------------------
class RelatedProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    price_text = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "image",
            "price", "discount_percent",
            "final_price", "price_text",
            "unit", "is_in_stock",
        ]

    def get_final_price(self, obj):
        if obj.discount_percent and obj.discount_percent > 0:
            discount = (obj.price * Decimal(obj.discount_percent)) / Decimal(100)
            return obj.price - discount
        return obj.price

    def get_price_text(self, obj):
        p = self.get_final_price(obj)
        return f"{p:,.0f}៛ / {obj.unit}" if obj.unit else f"{p:,.0f}៛"


# -----------------------------------------
# Product Serializer (LIST) - Fast response
# -----------------------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True
    )

    final_price = serializers.SerializerMethodField()
    price_text = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id","name","slug","sku","image",
            "price","discount_percent","final_price","price_text",
            "stock","is_in_stock","is_new","is_featured","is_active",
            "description","unit","created_at","updated_at",
            "category","category_id",
        ]

    def get_final_price(self, obj):
        if obj.discount_percent and obj.discount_percent > 0:
            discount = (obj.price * Decimal(obj.discount_percent)) / Decimal(100)
            return obj.price - discount
        return obj.price

    def get_price_text(self, obj):
        p = self.get_final_price(obj)
        return f"{p:,.0f}៛ / {obj.unit}" if obj.unit else f"{p:,.0f}៛"


class ProductDetailSerializer(ProductSerializer):
    related_products = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["related_products"]

    def get_related_products(self, obj):
        if not obj.category_id:
            return []
        qs = (
            Product.objects
            .filter(category_id=obj.category_id, is_active=True)
            .exclude(id=obj.id)
            .order_by("-created_at")[:10]
        )
        return RelatedProductSerializer(qs, many=True, context=self.context).data


# ==========================
# ✅ CART SERIALIZERS
# ==========================
class CartProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    price_text = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id","name","image",
            "price","discount_percent",
            "final_price","price_text",
            "unit","is_in_stock",
        ]

    def get_final_price(self, obj):
        if obj.discount_percent and obj.discount_percent > 0:
            discount = (obj.price * Decimal(obj.discount_percent)) / Decimal(100)
            return obj.price - discount
        return obj.price

    def get_price_text(self, obj):
        p = self.get_final_price(obj)
        return f"{p:,.0f}៛ / {obj.unit}" if obj.unit else f"{p:,.0f}៛"


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.all(),
        write_only=True
    )
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "qty", "line_total"]

    def get_line_total(self, obj):
        return Decimal(obj.qty) * Decimal(obj.product.final_price)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total"]

    def get_total(self, cart: Cart):
        total = Decimal("0")
        for it in cart.items.select_related("product").all():
            total += Decimal(it.qty) * Decimal(it.product.final_price)
        return total
