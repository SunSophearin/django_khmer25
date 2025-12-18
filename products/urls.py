from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    CartItemViewSet,
)

router = DefaultRouter()

# ✅ existing
router.register("categories", CategoryViewSet, basename="categories")
router.register("products", ProductViewSet, basename="products")

# ✅ cart
router.register("cart", CartViewSet, basename="cart")
router.register("cart/items", CartItemViewSet, basename="cart-items")

urlpatterns = router.urls
