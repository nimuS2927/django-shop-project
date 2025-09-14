import re

import django_filters
from django_filters.filterset import BaseFilterSet
from django_filters.filterset import FilterSetMetaclass
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from shop.models import Category
from shop.models import Product
from shop.models import Promotion


def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class CamelCaseDjangoFilterBackend(DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        kwargs = super().get_filterset_kwargs(request, queryset, view)

        data = kwargs["data"]
        new_data = {}

        for k, v in data.items():
            new_data[camel_to_snake(k)] = v

        kwargs["data"] = new_data
        return kwargs


class CustomOrderingFilter(OrderingFilter):
    ordering_param = "sort"
    ordering_type = "sortType"

    def get_ordering(self, request, queryset, view):
        """
        Ordering is set by a comma delimited ?ordering=... query parameter.
        The `ordering` query parameter can be overridden by setting
        the `ordering_param` value on the OrderingFilter or by
        specifying an `ORDERING_PARAM` value in the API settings.

        Можно сортировать по нескольким полям через запятую, а также использовать
        sortType для управления поведением сортировки
            des - сортировка по убыванию,
            asc - сортировка по возрастанию (по стандарту)
            sortType может содержать 1 параметр и тогда он будет применен ко всем полям
            или столько же параметров как и количество переданных полей в sort
            и тогда к каждому полю будет применен индивидуальный порядок сортировки
        """
        params = request.query_params.get(self.ordering_param)
        if params:
            fields = [param.strip() for param in params.split(",")]
            ordering = self.remove_invalid_fields(queryset, fields, view, request)
            if ordering:
                sort_type_str = request.query_params.get(self.ordering_type)

                if sort_type_str is None:
                    return ordering

                sort_types = [
                    sort_type.strip() for sort_type in sort_type_str.split(",")
                ]

                if len(sort_types) == 1 and sort_types[0] == "des":
                    return [f"-{field}" for field in ordering]

                if len(sort_types) == len(ordering):
                    return [
                        f"-{field}" if sort_type == "des" else field
                        for field, sort_type in zip(ordering, sort_types, strict=True)
                    ]
                return ordering

        # No ordering was included, or all the ordering fields were invalid
        return self.get_default_ordering(view)


class CustomDFFilterSet(BaseFilterSet, metaclass=FilterSetMetaclass):
    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class ProductFilter(CustomDFFilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_count = django_filters.NumberFilter(field_name="count", lookup_expr="gte")
    max_count = django_filters.NumberFilter(field_name="count", lookup_expr="lte")
    available = django_filters.BooleanFilter(field_name="available")
    promotion = django_filters.BooleanFilter(method="filter_promotions")
    tags = NumberInFilter(field_name="tags", lookup_expr="in")

    category_id = django_filters.NumberFilter(method="filter_category")

    class Meta:
        model = Product
        fields = [
            "title",
            "description",
            "min_price",
            "max_price",
            "min_count",
            "max_count",
            "available",
            "category_id",
            "tags",
        ]

    @staticmethod
    def filter_category(queryset, name, value):
        """
        Фильтр возвращает запрошенную категорию, а также всех ее подкатегорий
        """
        try:
            category = Category.objects.get(id=value)
        except Category.DoesNotExist:
            return queryset.none()

        descendants = category.get_descendants(include_self=True)
        return queryset.filter(category__in=descendants)

    def filter_promotions(self, queryset, name, value):
        if value in [None, False]:  # наличие акции не фильтруется
            return queryset
        return queryset.filter(promotions__in=Promotion.objects.active()).distinct()


class PromotionFilter(CustomDFFilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )
    min_discount_percent = django_filters.NumberFilter(
        field_name="discount_percent", lookup_expr="gte"
    )
    max_discount_percent = django_filters.NumberFilter(
        field_name="discount_percent", lookup_expr="lte"
    )
    is_active = django_filters.BooleanFilter(field_name="is_active")
    start_date = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        model = Promotion
        fields = [
            "title",
            "description",
            "min_discount_percent",
            "max_discount_percent",
            "is_active",
            "start_date",
            "end_date",
        ]
