from django.contrib.auth import get_user_model
from rest_framework import pagination
from rest_framework import serializers
from rest_framework.response import Response

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

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "name"]


class ImageCategorySerializer(serializers.ModelSerializer):
    src = serializers.URLField(source="src.url")

    class Meta:
        model = ImageCategory
        fields = ["src", "alt"]


class SubCategorySerializer(serializers.ModelSerializer):
    image = ImageCategorySerializer(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "image"]


class CategorySerializer(serializers.ModelSerializer):
    image = ImageCategorySerializer(read_only=True)
    subcategories = SubCategorySerializer(
        "self.get_children", many=True, read_only=True
    )

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]


class RecursiveCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    subcategories = serializers.SerializerMethodField(required=False)
    image = ImageCategorySerializer(read_only=True, required=False)

    def get_subcategories(self, obj):
        serializer = RecursiveCategorySerializer(obj["subcategories"], many=True)
        return serializer.data


class ImageProductSerializer(serializers.ModelSerializer):
    src = serializers.URLField(source="src.url")

    class Meta:
        model = ImageProduct
        fields = ["src", "alt"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class PromotionSerializer(serializers.ModelSerializer):
    short_description = serializers.CharField(
        read_only=True, required=False, source="get_short_description"
    )
    is_valid = serializers.BooleanField()

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "discount_percent",
            "description",
            "short_description",
            "start_date",
            "end_date",
            "is_active",
            "is_valid",
        ]
        extra_kwargs = {
            "is_active": {"help_text": "Статус действия акции."},
            "is_valid": {
                "help_text": (
                    "True - если акция активна, а также start_date < now < end_date."
                )
            },
        }


class PromotionProductSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(read_only=True)
    available_for_sale = serializers.BooleanField()

    class Meta:
        model = PromotionProduct
        fields = [
            "id",
            "limit",
            "quantity_sold",
            "price_with_discount",
            "available_for_sale",
            "promotion",
        ]
        extra_kwargs = {
            "available_for_sale": {
                "help_text": "Количество товара доступного для продажи."
            },
        }


class ProductSerializer(serializers.ModelSerializer):
    available = serializers.BooleanField()
    images = ImageProductSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
    price_with_promotions = serializers.DecimalField(
        source="get_price_with_promotions", max_digits=8, decimal_places=2
    )
    short_description = serializers.CharField(
        read_only=True, required=False, source="get_short_description"
    )
    promotions = PromotionProductSerializer(
        source="promotion_products", many=True, read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "price",
            "count",
            "description",
            "short_description",
            "available",
            "quantity_sold",
            "price_with_promotions",
            "images",
            "tags",
            "promotions",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "count", "price"]


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "user", "items"]


class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = BasketItem
        fields = ["id", "product", "count", "price"]


class BasketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = BasketItemSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = ["id", "user", "items"]


class DefaultPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = "limit"

    def get_paginated_response(self, data):
        return Response(
            {
                "items": data,
                "currentPage": self.page.number,
                "lastPage": self.page.paginator.num_pages,
            }
        )
