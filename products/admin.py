from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("parent__id", "id")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id", "image_preview", "name", "category",
        "price", "discount_percent", "stock",
        "is_new", "is_featured", "is_active", "created_at",
    )

    list_filter = ("category", "is_new", "is_featured", "is_active")
    search_fields = ("name", "slug", "sku")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")
    list_editable = ("price", "stock", "is_new", "is_featured", "is_active")
    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Info", {"fields": ("name", "slug", "sku", "category")}),
        ("Image", {"fields": ("image", "image_preview")}),
        ("Pricing", {"fields": ("price", "discount_percent")}),
        ("Stock & Status", {"fields": ("stock", "is_in_stock", "is_new", "is_featured", "is_active")}),
        ("Description", {"fields": ("description", "unit")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" style="border-radius:8px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"
