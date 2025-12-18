from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category_khmer25/", blank=True, null=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE,
        null=True, blank=True, related_name="subcategories"
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="products_khmer25/", blank=True, null=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(default=0)

    stock = models.PositiveIntegerField(default=0)
    is_in_stock = models.BooleanField(default=True)

    is_new = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def final_price(self):
        if self.discount_percent and self.discount_percent > 0:
            return self.price * (100 - self.discount_percent) / 100
        return self.price

    def save(self, *args, **kwargs):
        self.is_in_stock = self.stock > 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ✅ Cart for logged-in user (Djoser)
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user.username})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="cart_items")
    qty = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="uniq_cart_product")
        ]

    def __str__(self):
        return f"{self.product.name} x{self.qty}"
