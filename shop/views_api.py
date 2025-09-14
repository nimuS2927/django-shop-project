from typing import Any

from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from shop.filters import ProductFilter
from shop.filters import PromotionFilter
from shop.models import Category
from shop.models import Product
from shop.models import Promotion
from shop.serializers import DefaultPagination
from shop.serializers import ProductSerializer
from shop.serializers import PromotionSerializer
from shop.serializers import RecursiveCategorySerializer


class CategoryApiView(ListAPIView):
    """Список всех категорий с древовидной структурой"""

    queryset = Category.objects.all().prefetch_related("image")
    serializer_class = RecursiveCategorySerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response([])

        tree = Category.build_tree(queryset)

        serializer = self.get_serializer(tree, many=True)
        return Response(serializer.data)


class CatalogAPIView(ListAPIView):
    """Каталог товаров доступных в магазине"""

    queryset = Product.objects.select_related("category").prefetch_related(
        "images", "tags", "promotion_products__promotion"
    )
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    serializer_class = ProductSerializer
    ordering_fields = ("price",)


class PromotionAPIView(ListAPIView):
    queryset = Promotion.objects.active()
    filterset_class = PromotionFilter
    serializer_class = PromotionSerializer
    pagination_class = DefaultPagination
