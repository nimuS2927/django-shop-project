from decimal import Decimal

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.db.models.query import Prefetch
from django.http import HttpRequest
from rest_framework.request import Request

from shop.models import Basket
from shop.models import BasketItem
from shop.models import Product


class SessionBasket:
    def __init__(self, request: Request | HttpRequest):
        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_ID)
        if not basket:
            basket = self.session[settings.BASKET_SESSION_ID] = {}
        self.basket = basket
        self.user = request.user if request.user.is_authenticated else None

    def __iter__(self):
        """
        Итерации по продуктам в корзине
        """
        products = Product.objects.filter(id__in=self.basket.keys())
        basket = self.basket.copy()
        for product in products:
            basket[str(product.id)]["product"] = product

        for item in basket.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["count"]
            yield item

    def __len__(self):
        return sum(item["count"] for item in self.basket.values())

    def add(self, product: Product, count=1, *, update_count=False):
        """
        Добавляет или обновляет товар в корзине
        """
        price = product.get_price_with_promotions()

        product_id = str(product.id)
        if product_id not in self.basket:
            self.basket[product_id] = {
                "count": 0,
                "price": str(price),
            }
        if update_count:
            self.basket[product_id]["count"] = count
        else:
            self.basket[product_id]["count"] += count
        self.save()

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * item["count"] for item in self.basket.values()
        )

    def clear(self):
        del self.session[settings.BASKET_SESSION_ID]
        self.save()

    def get_product_id(self):
        return [int(pid) for pid in self.basket]

    def refresh_prices(self):
        """
        Пересчитывает цены всех товаров в корзине с учётом текущих акций.
        """
        product_ids = self.get_product_id()
        products = Product.objects.filter(id__in=product_ids).prefetch_related(
            "promotions"
        )

        product_map = {str(p.id): p for p in products}

        for pid, item in self.basket.items():
            product = product_map.get(pid)
            if not product:
                continue
            new_price = product.get_price_with_promotions()
            item["price"] = str(new_price)

        self.save()

    def sync_to_db(self):
        """
        Сбрасывает корзину из сессии в базу (при выходе пользователя).
        """
        if not self.user or not self.user.is_authenticated:
            return

        basket, _ = Basket.objects.get_or_create(user=self.user)

        # очистим старое содержимое
        basket.items.all().delete()

        self.refresh_prices()

        for product_id, item in self.basket.items():
            BasketItem.objects.create(
                basket=basket,
                product_id=int(product_id),
                count=item["count"],
                price=Decimal(item["price"]),
            )

    def sync_from_db(self):
        """
        Загружаем корзину из базы в сессию (при входе пользователя).
        Если в сессии уже есть товары — оставляем их приоритетными.
        """
        if not self.user or not self.user.is_authenticated:
            return

        try:
            basket = Basket.objects.prefetch_related(
                Prefetch("items", queryset=BasketItem.objects.select_related("product"))
            ).get(user=self.user)

        except Basket.DoesNotExist:
            return

        for item in basket.items.all():
            product_id = str(item.product_id)

            # приоритет у сессии
            if product_id not in self.basket:
                self.basket[product_id] = {
                    "count": item.count,
                    "price": str(item.price),
                }

        self.refresh_prices()
        self.save()

    def save(self):
        """
        Сохраняет корзину
        """
        self.session.modified = True

    def remove(self, product_id: int, count=1):
        """
        Удаляет продукт из корзины
        """
        s_product_id = str(product_id)
        if s_product_id in self.basket:
            if count == self.basket[s_product_id]["count"]:
                del self.basket[s_product_id]
            else:
                self.basket[s_product_id]["count"] -= count
            self.save()


def load_basket_on_login(sender, request, user, **kwargs):
    basket = SessionBasket(request)
    basket.sync_from_db()


user_logged_in.connect(load_basket_on_login)


def save_basket_on_logout(sender, request, user, **kwargs):
    basket = SessionBasket(request)
    basket.sync_to_db()


user_logged_out.connect(save_basket_on_logout)
