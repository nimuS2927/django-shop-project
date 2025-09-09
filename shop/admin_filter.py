from decimal import Decimal
from decimal import InvalidOperation

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest


class MinPriceFilter(admin.SimpleListFilter):
    title = "Мин. цена"
    parameter_name = "min_price"
    template = "admin/min_price_filter.html"

    def lookups(self, request, model_admin):
        return []

    def has_output(self) -> bool:
        return True

    def queryset(
        self,
        request: HttpRequest,
        queryset: QuerySet,
    ) -> QuerySet:
        raw_min: str | None = request.GET.get(self.parameter_name)
        try:
            min_price = Decimal(raw_min) if raw_min not in (None, "") else None
        except (InvalidOperation, TypeError, ValueError):
            min_price = None
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        return queryset


class MaxPriceFilter(admin.SimpleListFilter):
    title = "Макс. цена"
    parameter_name = "max_price"
    template = "admin/max_price_filter.html"

    def lookups(self, request, model_admin):
        return []

    def has_output(self) -> bool:
        return True

    def queryset(
        self,
        request: HttpRequest,
        queryset: QuerySet,
    ) -> QuerySet:
        raw_max: str | None = request.GET.get(self.parameter_name)
        try:
            max_price = Decimal(raw_max) if raw_max not in (None, "") else None
        except (InvalidOperation, TypeError, ValueError):
            max_price = None
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        return queryset
