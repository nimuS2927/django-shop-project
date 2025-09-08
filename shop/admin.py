from django.contrib import admin

from shop.models import Basket
from shop.models import BasketItem
from shop.models import Category
from shop.models import ImageCategory
from shop.models import ImageProduct
from shop.models import Order
from shop.models import OrderItem
from shop.models import Product
from shop.models import Promotion
from shop.models import PromotionProduct
from shop.models import Tag


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ("product", "count", "price", "total_price")
    readonly_fields = ("total_price",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_cost")
    list_display_links = "id", "user"
    ordering = "user", "id", "status"
    search_fields = ("user",)
    inlines = [OrderItemInline]


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    extra = 1
    fields = ("product", "count", "price", "total_price")
    readonly_fields = ("total_price",)


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_cost")
    list_display_links = "id", "user"
    ordering = "user", "id"
    search_fields = ("user",)
    inlines = [BasketItemInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "parent",
        "get_children",
    )
    list_display_links = "id", "parent"
    ordering = ("id",)
    search_fields = ("title",)

    @admin.display(description="Подкатегории")
    def get_children(self, obj):
        return ", ".join(child.title for child in obj.children.all())


@admin.register(ImageCategory)
class ImageCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "src",
        "alt",
        "category",
    )
    list_display_links = "id", "src"
    ordering = (
        "category",
        "id",
    )
    search_fields = (
        "alt",
        "category",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "price",
        "count",
        "quantity_sold",
        "available",
        "get_short_description",
    )
    list_display_links = "id", "title"
    ordering = (
        "title",
        "available",
        "price",
    )
    search_fields = (
        "title",
        "get_short_description",
    )


@admin.register(ImageProduct)
class ImageProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "src",
        "alt",
        "product",
    )
    list_display_links = "id", "src"
    ordering = (
        "product",
        "id",
    )
    search_fields = (
        "alt",
        "product",
    )


class PromotionProductInline(admin.StackedInline):
    model = PromotionProduct
    extra = 1
    fields = (
        "id",
        "product",
        "limit",
        "quantity_sold",
        "price_with_discount",
    )
    readonly_fields = ("price_with_discount",)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "get_short_description",
        "discount_percent",
        "start_date",
        "end_date",
        "is_active",
    )
    list_display_links = "id", "title"
    ordering = (
        "is_active",
        "title",
    )
    search_fields = (
        "title",
        "get_short_description",
    )
    inlines = [PromotionProductInline]


class ProductInline(admin.TabularInline):
    model = Tag.products.through
    extra = 1
    fields = ("product",)
    verbose_name = "Товар"
    verbose_name_plural = "Товары"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = "id", "name"
    ordering = ("name",)
    search_fields = ("name",)
    inlines = [ProductInline]
