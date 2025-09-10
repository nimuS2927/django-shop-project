from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

User = get_user_model()
MAX_DESCRIPTION_LENGTH = 50
ATTR_ERR_MSG = "Модель не имеет необходимых полей"


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        abstract = True


class IDMixin(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, verbose_name="ID")

    class Meta:
        abstract = True


class TotalPriceMixin:
    def total_price(self):
        if hasattr(self, "count") and hasattr(self, "price"):
            if self.count and self.price:
                return self.count * self.price
            return "-"
        raise AttributeError(ATTR_ERR_MSG)

    total_price.short_description = "Сумма"


class TotalCostMixin:
    def total_cost(self):
        if hasattr(self, "items"):
            items = self.items.all()
            if items and len(items) > 0:
                return sum([i.total_price() for i in items])
            return "-"
        raise AttributeError(ATTR_ERR_MSG)

    total_cost.short_description = "Общая сумма заказа"


class ShortDescriptionMixin:
    def get_short_description(self):
        if hasattr(self, "description"):
            if len(self.description) > MAX_DESCRIPTION_LENGTH:
                return self.description[:MAX_DESCRIPTION_LENGTH] + "..."
            return self.description
        raise AttributeError(ATTR_ERR_MSG)

    get_short_description.short_description = "Краткое описание"


class Category(IDMixin, TimestampMixin, MPTTModel):
    title = models.CharField(
        max_length=100,
        blank=False,
        verbose_name="Название",
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
        verbose_name="Родительская категория",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    class MPTTMeta:
        order_insertion_by = ["title"]

    def __str__(self):
        return f"ID: {self.id} | {self.title}"


def path_to_category_image(instance: "ImageCategory", filename: str) -> str:
    return f"category_{instance.category_id}/images/{filename}"


class ImageCategory(IDMixin, TimestampMixin, models.Model):
    src = models.ImageField(
        null=True,
        blank=True,
        upload_to=path_to_category_image,
        verbose_name="Путь до изображения",
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
        default="Описание для изображения не добавлено",
        verbose_name="Описание изображения",
    )
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name="image",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Изображение категории"
        verbose_name_plural = "Изображения категорий"
        ordering = ["category__title"]

    def __str__(self):
        return str(self.src)


class Product(IDMixin, TimestampMixin, ShortDescriptionMixin, models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )
    price = models.DecimalField(
        blank=True,
        max_digits=8,
        decimal_places=2,
        verbose_name="Цена",
    )
    count = models.PositiveSmallIntegerField(
        blank=True,
        default=1,
        verbose_name="Количество на складе",
    )
    title = models.CharField(
        max_length=100,
        blank=False,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    available = models.BooleanField(
        default=True,
        verbose_name="Доступно к продаже",
    )
    quantity_sold = models.SmallIntegerField(
        default=0,
        verbose_name="Всего продано",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} - {self.price} Руб."

    def get_available(self):
        self.available = self.count > 0
        self.save()
        return self.available

    def get_tags_list(self):
        if self.tags is not None:
            return list(self.tags.all())
        return []

    get_tags_list.short_description = "Список тегов"

    def get_images(self):
        return [
            {
                "src": image.src.url,
                "alt": image.alt,
            }
            for image in self.images.all()
        ]

    def get_price_with_promotions(self):
        """
        Возвращает цену с учётом активных акций.
        """
        price = self.price
        promotions = self.promotions.all()
        if promotions:
            prices_with_discount = [
                promo.apply_price_with_discount(price)
                for promo in self.promotions.all()
            ]
            price = min(prices_with_discount)
        return price


def path_to_product_image(instance: "ImageProduct", filename: str) -> str:
    return f"product_{instance.product_id}/images/{filename}"


class ImageProduct(IDMixin, TimestampMixin, models.Model):
    src = models.ImageField(
        null=True,
        blank=True,
        upload_to=path_to_product_image,
        verbose_name="Путь до изображения",
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
        default="Описание для изображения не добавлено",
        verbose_name="Описание изображения",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Продукты",
    )

    class Meta:
        verbose_name = "Изображения продукта"
        verbose_name_plural = "Изображения продуктов"
        ordering = ["product__title"]

    def __str__(self):
        return str(self.src)


class Tag(IDMixin, TimestampMixin, models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, related_name="tags")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PromotionProduct(IDMixin, TimestampMixin, models.Model):
    promotion = models.ForeignKey(
        "Promotion",
        on_delete=models.CASCADE,
        verbose_name="Акция",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        verbose_name="Товар",
    )
    limit = models.SmallIntegerField(
        verbose_name="Лимит продаж по акции",
        default=None,
        blank=True,
        null=True,
    )
    quantity_sold = models.SmallIntegerField(
        default=0,
        verbose_name="Всего продано по акции",
    )
    price_with_discount = models.DecimalField(
        verbose_name="Цена в акции",
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=True,
    )

    class Meta:
        unique_together = ("promotion", "product")
        verbose_name = "Товар в акции"
        verbose_name_plural = "Товары в акции"

    def __str__(self):
        return f"{self.product} в {self.promotion}"

    def save(self, *args, **kwargs):
        if self.price_with_discount in [None, ""]:
            self.price_with_discount = self.promotion.apply_price_with_discount(
                self.product.price
            )
        super().save(*args, **kwargs)

    def available_for_sale(self):
        return (
            999  # Продажа не ограничена
            if self.limit in [None, 0]
            else self.limit - self.quantity_sold
        )


class Promotion(IDMixin, TimestampMixin, ShortDescriptionMixin, models.Model):
    title = models.CharField(verbose_name="Название акции", max_length=255)
    description = models.TextField(verbose_name="Описание", blank=True)
    products = models.ManyToManyField(
        "Product",
        through="PromotionProduct",
        related_name="promotions",
        verbose_name="Товары",
    )
    discount_percent = models.PositiveSmallIntegerField(
        verbose_name="Скидка (%)",
        null=True,
        blank=True,
    )
    start_date = models.DateTimeField(verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        return self.title

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def apply_price_with_discount(self, price: Decimal) -> Decimal:
        """
        Возвращает цену со скидкой, если акция активна и условия выполнены.
        """
        if not self.is_valid():
            return price
        if self.discount_percent:
            discount = (price * Decimal(self.discount_percent)) / Decimal(100)
            return price - discount
        return price


class Basket(IDMixin, TimestampMixin, models.Model, TotalCostMixin):
    """
    Класс описывающий корзину, используется только для авторизованных пользователей
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name="basket",
        verbose_name="Корзина",
    )

    class Meta:
        ordering = ["user_id"]
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.user}"


class BasketItem(IDMixin, TimestampMixin, models.Model, TotalPriceMixin):
    basket = models.ForeignKey(
        Basket,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="basket_items",
        verbose_name="Товар",
    )
    count = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=False,
        verbose_name="Цена",
    )

    class Meta:
        unique_together = ("basket", "product")
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"

    def __str__(self):
        return f"{self.product} x {self.count}"

    def save(self, *args, **kwargs):
        if self.price in [None, ""]:
            self.price = self.product.get_price_with_promotions()
        super().save(*args, **kwargs)


class OrderStatus(models.TextChoices):
    CREATED = "оформлен"
    PAID = "оплачен"
    COMPLETED = "завершен"
    CANCELLED = "отменен"


class Order(IDMixin, TimestampMixin, models.Model, TotalCostMixin):
    user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    status = models.CharField(
        max_length=16,
        choices=OrderStatus,
        default=OrderStatus.CREATED,
        verbose_name="Статус заказа",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Пользователь {self.user} / Заказ ID - {self.id} "

    def set_status(self, status: OrderStatus) -> None:
        self.status = status
        self.save()

    def mark_paid(self):
        self.set_status(OrderStatus.PAID)

    def mark_completed(self):
        self.set_status(OrderStatus.COMPLETED)

    def mark_cancelled(self):
        self.set_status(OrderStatus.CANCELLED)


class OrderItem(IDMixin, TimestampMixin, models.Model, TotalPriceMixin):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Товар",
    )
    count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Количество",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=False,
        verbose_name="Цена",
    )

    class Meta:
        unique_together = ("order", "product")
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    def __str__(self):
        return f"{self.product} x {self.count}"

    def save(self, *args, **kwargs):
        if self.price in [None, ""]:
            self.price = self.product.get_price_with_promotions()
        super().save(*args, **kwargs)
