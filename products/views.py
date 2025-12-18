from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Category, Product, Cart, CartItem
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
    CartSerializer,
    CartItemSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["id", "name"]
    ordering = ["id"]

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True).order_by("id")


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related("category")

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug", "sku"]
    ordering_fields = ["id", "price", "created_at"]
    ordering = ["-id"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    def get_queryset(self):
        """
        Query params:
        - ?is_new=true
        - ?is_featured=true
        - ?discounted=true   (discount_percent > 0)
        - ?category=ID
        - ?parent_category=ID  (products in subcategories under a parent category)
        """
        qs = Product.objects.filter(is_active=True).select_related("category")
        q = self.request.query_params

        if q.get("is_new") in ["true", "1", "yes"]:
            qs = qs.filter(is_new=True)

        if q.get("is_featured") in ["true", "1", "yes"]:
            qs = qs.filter(is_featured=True)

        if q.get("discounted") in ["true", "1", "yes"]:
            qs = qs.filter(discount_percent__gt=0)

        if q.get("category"):
            qs = qs.filter(category_id=q.get("category"))

        if q.get("parent_category"):
            qs = qs.filter(category__parent_id=q.get("parent_category"))

        return qs.order_by("-id")


# ==========================
# ✅ CART API (ViewSets)
# ==========================

def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartViewSet(viewsets.ViewSet):
    """
    Endpoints:
    - GET  /api/cart/                 => get my cart
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart = get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data, status=200)


class CartItemViewSet(viewsets.ViewSet):
    """
    Endpoints:
    - POST   /api/cart/items/         body: {product_id, qty}  => add to cart
    - PATCH  /api/cart/items/<id>/    body: {qty}              => update qty
    - DELETE /api/cart/items/<id>/    => remove item
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        cart = get_or_create_cart(request.user)

        product_id = request.data.get("product_id")
        qty = int(request.data.get("qty", 1))

        if not product_id:
            return Response({"detail": "product_id is required"}, status=400)
        if qty < 1:
            return Response({"detail": "qty must be >= 1"}, status=400)

        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return Response({"detail": "Product not found"}, status=404)

        if product.stock < qty:
            return Response({"detail": "Not enough stock"}, status=400)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.qty = qty if created else (item.qty + qty)

        if product.stock < item.qty:
            return Response({"detail": "Not enough stock"}, status=400)

        item.save()
        return Response(CartSerializer(cart).data, status=200)

    def partial_update(self, request, pk=None):
        cart = get_or_create_cart(request.user)

        item = CartItem.objects.filter(id=pk, cart=cart).select_related("product").first()
        if not item:
            return Response({"detail": "Item not found"}, status=404)

        qty = int(request.data.get("qty", item.qty))

        if qty < 1:
            item.delete()
        else:
            if item.product.stock < qty:
                return Response({"detail": "Not enough stock"}, status=400)
            item.qty = qty
            item.save()

        return Response(CartSerializer(cart).data, status=200)

    def destroy(self, request, pk=None):
        cart = get_or_create_cart(request.user)

        item = CartItem.objects.filter(id=pk, cart=cart).first()
        if not item:
            return Response({"detail": "Item not found"}, status=404)

        item.delete()
        return Response(CartSerializer(cart).data, status=200)
